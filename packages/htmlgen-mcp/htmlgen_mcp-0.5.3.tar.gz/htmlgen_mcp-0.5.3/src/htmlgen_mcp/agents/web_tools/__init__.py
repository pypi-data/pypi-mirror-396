"""网页工具包 - 仅保留 EdgeOne 部署工具"""

from .edgeone_deploy import deploy_folder_or_zip_to_edgeone, EdgeOneDeployer

__all__ = [
    "deploy_folder_or_zip_to_edgeone",
    "EdgeOneDeployer",
]
