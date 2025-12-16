from baicai_dev.utils.data import TaskType

from baicai_webui.components.base_page import BasePage
from baicai_webui.components.model import nlp_uploader


def show():
    """显示自然语言处理任务页面"""
    page = BasePage(TaskType.NLP, nlp_uploader)
    page.show(title="自然语言处理")

show()