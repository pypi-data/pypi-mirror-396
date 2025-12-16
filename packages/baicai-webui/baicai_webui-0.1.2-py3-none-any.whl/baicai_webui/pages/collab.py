from baicai_dev.utils.data import TaskType

from baicai_webui.components.base_page import BasePage
from baicai_webui.components.model import collab_uploader


def show():
    """显示协同过滤任务页面"""
    page = BasePage(TaskType.COLLABORATIVE, collab_uploader)
    page.show(title="协同过滤")

show()
