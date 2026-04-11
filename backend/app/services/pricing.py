from app.schemas.user import MemberPrice


_MEMBER_PRICES = [
    MemberPrice(level="vip", name="VIP会员", price=2900, duration=30, features=[
        "无限次AI对话",
        "无限次MBTI测试",
        "专属AI助手",
        "情感日记",
        "知识库VIP内容",
    ]),
    MemberPrice(level="svip", name="超级会员", price=9900, duration=90, features=[
        "VIP全部权益",
        "优先响应",
        "专属情感顾问",
        "线下活动资格",
        "会员专属折扣",
    ]),
    MemberPrice(level="enterprise", name="企业会员", price=39900, duration=365, features=[
        "SVIP全部权益",
        "企业API接口",
        "定制AI助手",
        "专属客服",
        "数据报告",
    ]),
]


def get_member_prices():
    return _MEMBER_PRICES
