"""
认证接口
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import redis.asyncio as redis
import loguru

from app.core.database import get_db, get_redis
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    generate_verify_code,
)
from app.core.config import settings
from app.models import User
from app.schemas.user import (
    SmsSendRequest,
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    UserInfo,
    ResetPasswordRequest,
)
from app.api.deps import get_current_user
from app.services.auth_service import generate_nickname
from app.services.sms_service import get_sms_service
from app.core.i18n import _

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/test_login", summary="测试登录（自动创建账号，仅开发环境）")
async def test_login(
    request: SmsSendRequest,
    db: Session = Depends(get_db),
):
    """测试登录：使用手机号直接登录，不存在则自动创建
    
    ⚠️ 仅在 DEBUG=True 时可用，不应存在于生产环境
    """
    from app.core.config import settings
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该接口仅在开发环境可用",
        )
    
    phone = request.phone

    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        # 仅开发环境使用默认密码，生产环境应使用随机密码并通过短信发送
        user = User(
            phone=phone,
            nickname=generate_nickname(),
            password_hash=get_password_hash("test123456"),
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        loguru.logger.warning(f"[SECURITY] 自动创建测试用户: {phone} - 仅开发环境")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用",
        )

    from datetime import datetime

    user.last_login_at = datetime.now()
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserInfo.model_validate(user),
    )


@router.post("/send_code", summary="发送验证码")
async def send_verify_code(
    request: SmsSendRequest,
    redis_client: redis.Redis = Depends(get_redis),
):
    """发送手机验证码"""
    # 生成验证码
    code = generate_verify_code(6)

    key = f"sms:code:{request.phone}"
    await redis_client.setex(key, 300, code)

    sms_service = get_sms_service()
    success = await sms_service.send_verify_code(request.phone, code)
    if not success:
        loguru.logger.error(f"短信发送失败: {request.phone}")

    return {"message": _("验证码已发送")}


@router.post("/register", summary="用户注册")
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """用户注册 - 支持手机号、邮箱、用户名注册"""
    # 验证必填字段
    if not request.password or len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_("密码长度至少6位"),
        )

    # 手机号注册需要验证码
    if request.phone:
        if not request.code or len(request.code) != 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_("验证码格式错误"),
            )

        redis_client = await get_redis()
        key = f"sms:code:{request.phone}"
        stored_code = await redis_client.get(key)
        if not stored_code or stored_code != request.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_("验证码错误或已过期"),
            )
        await redis_client.delete(key)

        # 检查手机号是否已存在
        existing_user = db.query(User).filter(User.phone == request.phone).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_("该手机号已注册"),
            )

    # 邮箱注册
    if request.email:
        # 检查邮箱是否已存在
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_("该邮箱已注册"),
            )

    # 用户名注册
    if request.username:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_("该用户名已被使用"),
            )

    # 确定昵称
    nickname = request.nickname
    if not nickname:
        if request.username:
            nickname = request.username
        else:
            nickname = generate_nickname()

    # 创建用户
    user = User(
        phone=request.phone,
        email=request.email,
        username=request.username,
        nickname=nickname,
        password_hash=get_password_hash(request.password),
        is_verified=bool(request.phone or request.email),  # 手机或邮箱验证过的用户标记为已验证
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserInfo.model_validate(user),
    )


@router.post("/login", summary="用户登录")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    identifier = request.identifier.strip()
    password = request.password

    # 根据identifier类型查找用户
    user = None
    if '@' in identifier:
        # 邮箱登录
        user = db.query(User).filter(User.email == identifier).first()
    elif identifier.isdigit() and len(identifier) == 11:
        # 手机号登录
        user = db.query(User).filter(User.phone == identifier).first()
    else:
        # 用户名登录
        user = db.query(User).filter(User.username == identifier).first()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_("账号或密码错误"),
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_("账号或密码错误"),
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_("账号已被禁用"),
        )

    from datetime import datetime

    user.last_login_at = datetime.now()
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserInfo.model_validate(user),
    )


@router.post("/refresh", summary="刷新令牌")
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    from jose import JWTError, jwt
    from fastapi import HTTPException, status

    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
            )
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return UserInfo.model_validate(current_user)


@router.post("/logout", summary="退出登录")
async def logout(
    current_user: User = Depends(get_current_user),
):
    return {"message": "退出成功"}


@router.post("/reset_password", summary="重置密码")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    """通过手机验证码重置密码"""
    # 验证验证码
    key = f"sms:code:{request.phone}"
    stored_code = await redis_client.get(key)

    if not stored_code or stored_code.decode() != request.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期"
        )

    # 查找用户
    user = db.query(User).filter(User.phone == request.phone).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 更新密码
    user.password_hash = get_password_hash(request.new_password)
    db.commit()
    db.refresh(user)

    # 删除验证码
    await redis_client.delete(key)

    return {"message": "密码重置成功"}


@router.get("/crisis-resources", summary="获取危机干预资源")
async def get_crisis_resources():
    """获取危机干预资源和求助热线"""
    return {
        "title": "危机干预求助资源",
        "description": "如果你正在经历心理危机，请立即寻求帮助",
        "hotlines": [
            {
                "name": "全国心理援助热线",
                "number": "400-161-9995",
                "description": "24小时免费心理援助热线",
                "url": "",
            },
            {
                "name": "北京心理危机研究与干预中心",
                "number": "800-810-1117",
                "description": "24小时危机干预热线",
                "url": "",
            },
            {
                "name": "希望24热线",
                "number": "400-161-9995",
                "description": "生命危机干预",
                "url": "http://www.hope24.org/",
            },
        ],
        "online_resources": [
            {
                "name": "简单心理 - 危机干预",
                "url": "https://www.jiandanxinli.com/crisis",
            },
            {"name": "KnowYourself", "url": "https://www.knowyourself.cc/"},
        ],
        "urgent_message": "如果你或你身边的人正面临立即的生命危险，请立即拨打120或110求助。",
        "self_help_tips": [
            "试着做几次深呼吸，放松身体",
            "告诉自己：这只是暂时的，情绪会过去的",
            "联系你信任的朋友或家人，告诉他们你的感受",
            "离开危险环境，去一个安全的地方",
            "记住：你值得被帮助，你不孤单",
        ],
    }
