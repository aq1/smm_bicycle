from .vk import VkService
from .facebook import FacebookService
from .telegram import TelegramService
from .twitter import TwitterService

VK, FACEBOOK, TWITTER, TELEGRAM = range(4)

SERVICES = [
    VkService,
    FacebookService,
    TwitterService,
    TelegramService,
]

SERVICES_CHOICES = [
    (VK, VkService),
    (FACEBOOK, FacebookService),
    (TWITTER, TwitterService),
    (TELEGRAM, TelegramService),
]
