import re
import json
import logging
import tempfile
from pathlib import Path
import git
import requests
from bs4 import BeautifulSoup
import traceback
import functools
import inspect
from typing import Callable, Any
from typing import List, Dict, Any, Optional

import requests.exceptions
from typing import Generator, Optional,Tuple

log=logging.getLogger(__name__)

def enter_and_leave_function(func: Callable) -> Callable:
    """
    函数调用日志装饰器：
    1. 记录函数入参、调用位置
    2. 正常执行时记录返回值
    3. 异常时记录完整堆栈（含函数内具体报错行数）
    """

    @functools.wraps(func)  # 保留原函数元信息（如 __name__、__doc__）
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 获取函数定义的文件路径和行号（基础位置信息）
        func_def_file = inspect.getsourcefile(func) or "unknown_file"
        func_def_file = func_def_file.split("/")[-1]
        func_def_line = inspect.getsourcelines(func)[1] if func_def_file != "unknown_file" else "unknown_line"
        log.info(
            f"[{func_def_file}: {func_def_line}]"
            f"[{func.__name__}()]"
            f"| args={args}, kwargs={kwargs}"
        )

        try:
            result = func(*args, **kwargs)
            log.info(
                f"[{func_def_file}: {func_def_line}]"
                f" finish run function {func.__name__}(), return value is: {result} "
            )
            return result

        except Exception as e:
            error_traceback = traceback.format_exc()

            log.error(
                f"[{func_def_file}: {func_def_line}]"
                f"failed to run function {func.__name__}() :Failed. "
                f"| error_type：{type(e).__name__} "
                f"| error_message：{str(e)} "
                f"| full_stack_trace：\n{error_traceback}",
                exc_info=False  # 已手动捕获堆栈，避免 logging 重复打印
            )
            raise  # 重新抛出异常，不中断原异常链路

    return wrapper

class Gitee():
    def __init__(self):
        self.__base_url= "https://gitee.com/api/v5"
        self.__access_token="aa6cb32539129acf5605793f91a1588c"

    def get_branches_list_by_repo(self,repo_name,owner_name):
        """
        获取仓库的所有分支
        :param repo_name: 仓库名称
        :param owner_name: 仓库所属空间地址(企业、组织或个人的地址
        :return:
        """
        url = f"{self.__base_url}/repos/{owner_name}/{repo_name}/branches"
        page=1
        parameters={
            "access_token":self.__access_token,
            "repo":repo_name,
            "owner":owner_name,
            "sort":"name",
            "direction":"asc",
            "page":page,
            "per_page":10
        }
        headers={
            "Content-Type":"application/json",
            "Accept":"application/json",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
        }
        branches=[]
        while True:
            response=requests.get(url,params=parameters,headers=headers)
            if response.status_code==200:
                data=response.json()
                for branch in data:
                    branches.append(branch["name"])
                page+=1
                parameters["page"]=page
                if len(data)==0:
                    return branches
            else:
                log.error(f"request url is {url}, parameters is {parameters},headers is {headers} failed, response status code is {response.status_code}")
                return branches

    def get_repo_name_and_repo_html_url_by_org(self,org_name):
        log.info(f"begin to get openEuler repo names and repo html urls by org {org_name}...")
        url = f"{self.__base_url}/orgs/{org_name}/repos"
        page=1
        parameters={
            "access_token":"aa6cb32539129acf5605793f91a1588c",
            "org":org_name,
            "page":page,
            "per_page":10,
            "type":"all"
        }
        headers={
            "Content-Type":"application/json",
            "Accept":"application/json",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
        }
        page=1
        log.info(f"begin to request url is {url}, parameters is {parameters},headers is {headers}...")
        while True:
            response=requests.get(url,params=parameters,headers=headers)
            if response.status_code==200:
                data=response.json()
                for repo in data:
                    yield repo["name"],repo["html_url"]
                page+=1
                parameters["page"]=page
                if len(data)==0:
                    break
            else:
                log.error(f"request url is {url}, parameters is {parameters},headers is {headers} failed, response status code is {response.status_code}")
                break

class OpenEuler():
    def __init__(self):
        pass

    def get_openEuler_repo_names_and_urls(
            self,
            os_version: str
    ) -> Generator[Tuple[str, str], None, None]:
        """
        从 Gitee 的 src-openEuler 组织中筛选出包含指定 openEuler 版本分支的仓库信息。

        函数通过调用 Gitee 相关接口，遍历 src-openEuler 组织下的所有仓库，
        检查仓库是否存在与目标 openEuler 版本匹配的分支，若存在则返回该仓库的名称和 HTML 地址。

        Args:
            os_version: 目标 openEuler 版本号（如 "24.03-LTS-SP2"），用于匹配仓库分支

        Yields:
            Generator[Tuple[str, str], None, None]:
                迭代返回符合条件的仓库信息元组：
                - 第一个元素：仓库名称（如 "kernel"）
                - 第二个元素：仓库的 HTML 访问地址（如 "https://gitee.com/src-openEuler/kernel"）

        Notes:
            依赖 Gitee 类的以下方法：
            - get_repo_name_and_repo_html_url_by_org(org_name: str): 用于获取指定组织下所有仓库的名称和 HTML 地址
            - get_branches_list_by_repo(repo_name: str, org_name: str): 用于获取指定仓库的所有分支名称列表
        """
        # 初始化 Gitee 接口操作实例
        log.info("正在初始化 Gitee 接口操作实例...")
        gitee = Gitee()

        # 遍历 src-openEuler 组织下的所有仓库（名称 + HTML 地址）
        for repo_name, repo_url in gitee.get_repo_name_and_repo_html_url_by_org("src-openEuler"):
            log.info(f"正在检查仓库: {repo_name}，地址: {repo_url}")

            # 获取当前仓库的所有分支列表
            branches = gitee.get_branches_list_by_repo(repo_name, "src-openEuler")
            # 处理无分支的异常情况
            if not branches:
                log.warning(f"仓库 {repo_name}（{repo_url}）未发现任何分支，已跳过")
                continue

            # 检查目标版本分支是否存在，存在则返回该仓库信息
            branch = f"openEuler-{os_version}"
            if branch in branches:
                log.info(f"仓库 {repo_name}（{repo_url}）已找到目标版本分支 {branch}")
                yield repo_name, repo_url

    def get_core_src_list(self):
        core_src_list=[]
        try:
            with open("openEuler_core_src.txt", "r",encoding="utf-8") as f:
                for line in f.readlines():
                    if not line.strip():
                        continue
                    line_segs = line.strip().split("|")
                    if len(line_segs)>=3:
                        core_src_list.append(line_segs[2].strip())
        except Exception as e:
            log.error(f"get core src list failed, error is {e}")
        finally:
            return core_src_list

    def get_rpm_name_from_full_name(self, rpm):
        rpm_clean = rpm.strip()

        # 移除结尾的 .rpm 后缀（忽略大小写）
        rpm_clean = re.sub(r"\.rpm$", "", rpm_clean, flags=re.IGNORECASE)
        # 移除结尾的架构后缀（x86_64/aarch64等，解决.oe2403sp2.x86_64的层级干扰）
        arch_pattern = r"\.(x86_64|aarch64|arm64|i386|noarch|ppc64le|s390x)$"
        rpm_clean = re.sub(arch_pattern, "", rpm_clean, flags=re.IGNORECASE)

        # 步骤2：核心正则匹配（精准提取包名，适配v前缀/发行版标识）
        # 正则逻辑：
        # ^(.+?)-        匹配包名（非贪婪），直到最后一个"-"
        # (?=            正向预查（不捕获），确保后面是版本段：
        #   (v\d|svn|rc|beta|alpha|dev|release|\d)  版本起始标识（v2/svn17115/1.0等）
        #   \w*           版本中间字符（数字/字母/下划线等）
        #   (\.|-|oe|el|centos|fc|sp)              版本中的分隔符/发行版标识（.oe2403sp2/-el8等）
        #   .*            版本剩余部分（兼容多级发行版，如oe2403sp2）
        # )
        pkg_pattern = r"^(.+?)-(?=(v\d|svn|rc|beta|alpha|dev|release|\d)\w*(\.|-|oe|el|centos|fc|sp).*$)"
        match = re.match(pkg_pattern, rpm_clean, re.IGNORECASE)

        # 步骤3：结果处理
        if match:
            pkg_name = match.group(1)
            log.debug(f"Extracted RPM name: {pkg_name} | Original: {rpm} | Cleaned: {rpm_clean}")
            return pkg_name
        else:
            log.warning(f"RPM name {rpm} does not match pattern (cleaned: {rpm_clean})")
            return None

    def get_openEuler_pkgs(
            self, os_version: str, os_arch: str, scope: str
    ) -> Generator[str, None, None]:
        """
        从 openEuler everything 源页面迭代        以迭代方式返回指定版本、架构的所有 RPM 包完整名称。

        Args:
            os_version: openEuler 版本号（如 "24.03-LTS-SP2"）
            os_arch: 系统架构（如 "x86_64", "aarch64"）
            scope: openEuler官方镜像源上软件包的范围，可选值 everything，epol，update
        Yields:
            str: RPM 包完整名称（如 "zvbi-devel-0.2.44-1.oe2403sp2.x86_64.rpm"）

        Raises:
            RuntimeError: 网络请求失败（如超时、404、500 等）
            ValueError: 页面解析失败（未找到任何 .rpm 包）
        """
        base_url_template = "https://dl-cdn.openeuler.openatom.cn/openEuler-{os_version}/{scope}/{os_arch}/Packages/"
        timeout = 15
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        target_url = base_url_template.format(os_version=os_version, os_arch=os_arch,scope= scope)

        try:
            with requests.Session() as session:
                session.mount('https://', requests.adapters.HTTPAdapter(
                    pool_connections=10,
                    pool_maxsize=10,
                    max_retries=3
                ))
                response = session.get(
                    url=target_url,
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=True
                )
                response.raise_for_status()
                html_content = response.text

        except requests.exceptions.RequestException as e:
            log.error(f"获取页面失败！URL: {target_url}, 错误: {str(e)}")
            return

        soup = BeautifulSoup(html_content, "html.parser")
        # 精确匹配.rpm链接，排除父目录和空链接
        pkg_links = soup.find_all(
            "a",
            href=lambda href: isinstance(href, str) and href.endswith(".rpm") and not href.startswith('../')
        )

        if not pkg_links:
            log.error(f"页面解析失败！URL: {target_url}, 未找到任何 .rpm 包")
            return

        for link in pkg_links:
            full_pkg_name = link.get("href", "").strip()
            if full_pkg_name:  # 过滤空字符串
                pkg_name=self.get_rpm_name_from_full_name(full_pkg_name)
                yield pkg_name,full_pkg_name

    def get_openEuler_everything_rpm_list(self, os_version: str, os_arch: str):
        all_rpm_list = []
        for rpm_name, _ in self.get_openEuler_pkgs(os_version, os_arch, "everything"):
            if rpm_name not in all_rpm_list:
                all_rpm_list.append(rpm_name)
        return all_rpm_list

    def get_openEuler_epol_rpm_list(self, os_version: str, os_arch: str):
        all_rpm_list = []
        for rpm_name, _ in self.get_openEuler_pkgs(os_version, os_arch, "EPOL"):
            if rpm_name not in all_rpm_list:
                all_rpm_list.append(rpm_name)
        return all_rpm_list

    def get_openEuler_update_rpm_list(self, os_version: str, os_arch: str):
        all_rpm_list = []
        for rpm_name, _ in self.get_openEuler_pkgs(os_version, os_arch, "update"):
            if rpm_name not in all_rpm_list:
                all_rpm_list.append(rpm_name)
        return all_rpm_list

    def get_openEuler_os_rpm_list(self, os_version: str, os_arch: str):
        all_rpm_list = []
        for rpm_name, _ in self.get_openEuler_pkgs(os_version, os_arch, "OS"):
            if rpm_name not in all_rpm_list:
                all_rpm_list.append(rpm_name)
        return all_rpm_list


    def get_openEuler_all_rpm_list(self, os_version: str, os_arch: str):
        """
        获取指定版本、架构的所有 RPM 包完整名称。s

        Args:
            os_version: openEuler 版本号（如 "24.03-LTS-SP2"）
            os_arch: 系统架构（如 "x86_64", "aarch64"）

        Returns:
            list[str]: 包完整名称列表（如 ["zvbi-devel-0.2.44-1.oe2403sp2.x86_64.rpm", ...]）
        """
        all_rpm_list=[]
        for rpm_name,_ in self.get_openEuler_pkgs(os_version, os_arch, "everything"):
            if rpm_name not in all_rpm_list:
                all_rpm_list.append(rpm_name)
        for rpm_name,_ in self.get_openEuler_pkgs(os_version, os_arch, "EPOL"):
            if rpm_name not in all_rpm_list:
                all_rpm_list.append(rpm_name)
        for rpm_name,_ in self.get_openEuler_pkgs(os_version, os_arch, "update"):
            if rpm_name not in all_rpm_list:
                all_rpm_list.append(rpm_name)
        for rpm_name,_ in self.get_openEuler_pkgs(os_version, os_arch, "OS"):
            if rpm_name not in all_rpm_list:
                all_rpm_list.append(rpm_name)
        return all_rpm_list

    def get_openEuler_os_rpm2src(self,os_version,os_arch):
        rpm2src_file_path=Path(__file__).resolve().parent / "pkg_info" / f"openEuler_{os_version}_{os_arch}_os.json"
        rpm2src_data=dict({})
        try:
            with open(rpm2src_file_path, "r",encoding="utf-8") as f:
                rpm2src_data = json.load(f)
        except FileNotFoundError:
            log.error(f"未找到 {rpm2src_file_path} 文件")
        except json.JSONDecodeError:
            log.error(f"{rpm2src_file_path} 文件格式错误")
        except Exception as e:
            log.error(f"{rpm2src_file_path} 文件读取错误: {str(e)}")
        finally:
            return rpm2src_data

    def get_openEuler_update_rpm2src(self,os_version,os_arch):
        rpm2src_file_path=Path(__file__).resolve().parent / "pkg_info" / f"openEuler_{os_version}_{os_arch}_update.json"
        rpm2src_data=dict({})
        try:
            with open(rpm2src_file_path, "r",encoding="utf-8") as f:
                rpm2src_data = json.load(f)
        except FileNotFoundError:
            log.error(f"未找到 {rpm2src_file_path} 文件")
        except json.JSONDecodeError:
            log.error(f"{rpm2src_file_path} 文件格式错误")
        except Exception as e:
            log.error(f"{rpm2src_file_path} 文件读取错误: {str(e)}")
        finally:
            return rpm2src_data

    def get_openEuler_everything_rpm2src(self,os_version,os_arch):
        rpm2src_file_path=Path(__file__).resolve().parent / "pkg_info" / f"openEuler_{os_version}_{os_arch}_everything.json"
        rpm2src_data=dict({})
        try:
            with open(rpm2src_file_path, "r",encoding="utf-8") as f:
                rpm2src_data = json.load(f)
        except FileNotFoundError:
            log.error(f"未找到 {rpm2src_file_path} 文件")
        except json.JSONDecodeError:
            log.error(f"{rpm2src_file_path} 文件格式错误")
        except Exception as e:
            log.error(f"{rpm2src_file_path} 文件读取错误: {str(e)}")
        finally:
            return rpm2src_data

    def get_openEuler_epol_rpm2src(self,os_version,os_arch):
        rpm2src_file_path=Path(__file__).resolve().parent / "pkg_info" / f"openEuler_{os_version}_{os_arch}_epol.json"
        rpm2src_data=dict({})
        try:
            with open(rpm2src_file_path, "r",encoding="utf-8") as f:
                rpm2src_data = json.load(f)
        except FileNotFoundError:
            log.error(f"未找到 {rpm2src_file_path} 文件")
        except json.JSONDecodeError:
            log.error(f"{rpm2src_file_path} 文件格式错误")
        except Exception as e:
            log.error(f"{rpm2src_file_path} 文件读取错误: {str(e)}")
        finally:
            return rpm2src_data

if __name__ == "__main__":
    # 初始化获取器
    # oe = OpenEuler()
    # rs = oe.get_openEuler_os_rpm2src("24.03-LTS-SP1", "x86_64")
    # print(len(rs.keys()))
    # rs = oe.get_openEuler_update_rpm2src("24.03-LTS-SP1", "x86_64")
    # print(len(rs.keys()))
    # rs=oe.get_core_src_list()
    # print(rs)
    # rpm=oe.get_rpm_name_from_full_name("texlive-footbib-doc-svn17115.2.0.7-3.oe2403sp2.noarch.rpm")
    # print(rpm)
    # rpm=oe.get_rpm_name_from_full_name("oeAware-manager-debuginfo-v2.1.1-3.oe2403sp2.x86_64.rpm")
    # print(rpm)
    # rpm=oe.get_rpm_name_from_full_name("texlive-fontware-20210325-10.oe2403sp2.x86_64.rpm")
    # print(rpm)
    # rpm=oe.get_rpm_name_from_full_name("nodejs-lodash-valuesin-3.10.1-1.oe2403sp2.noarch.rpm")
    # print(rpm)
    # rs=oe.get_openEuler_everything_rpm_list("24.03-LTS-SP2", "x86_64")
    # print(f"everything {len(rs)} pkgs")
    # rs=oe.get_openEuler_epol_rpm_list("24.03-LTS-SP2", "x86_64")
    # print(f"epol {len(rs)} pkgs")
    # rs=oe.get_openEuler_update_rpm_list("24.03-LTS-SP2", "x86_64")
    # print(f"update {len(rs)} pkgs")
    # rs=oe.get_openEuler_os_rpm_list("24.03-LTS-SP2", "x86_64")
    # print(f"os {len(rs)} pkgs")
    # rs=oe.get_openEuler_all_rpm_list("24.03-LTS-SP2", "x86_64")
    # print(f"total {len(rs)} pkgs")

    # count=0
    # effective_count=0
    # for rpm_name,rpm_full_name in oe.get_openEuler_pkgs("24.03-LTS-SP1", "x86_64", "everything"):
    #     count+=1
    #     # print(f"{rpm_name}：{rpm_full_name}")
    # print(f"everything 共获取到 {count} 个包")
    # count = 0
    # for rpm_name,rpm_full_name in oe.get_openEuler_pkgs("24.03-LTS-SP1", "x86_64", "EPOL"):
    #     count+=1
    #     # print(f"{rpm_name}：{rpm_full_name}")
    # print(f"EPOL 共获取到 {count} 个包")
    # count = 0
    # for rpm_name,rpm_full_name in oe.get_openEuler_pkgs("24.03-LTS-SP1", "x86_64", "update"):
    #     count+=1
    #     # print(f"{rpm_name}：{rpm_full_name}")
    # print(f"update 共获取到 {count} 个包")
    # for rpm in oe.get_openEuler_rpm_names_from_repo("24.03-LTS-SP2", "python-minio","https://gitee.com/src-openeuler/python-minio.git"):
    #     print(f"src_name:python-minio,rpm:{rpm}")
    # log.info("正在初始化 Gitee 模块...")
    # repos_generator = oe.get_openEuler_repo_names_and_urls(
    #     os_version="24.03-LTS-SP2"
    # )
    # log.info("正在获取 openEuler 24.03-LTS-SP2 x86_64 架构的仓库信息...")
    # count=0
    # for repo_name, repo_url in repos_generator:
    #     log.info(f"正在处理仓库: {repo_name}，地址: {repo_url}")
    #     count+=1
    #     print(f"{repo_name}：{repo_url}")
    # log.info("共获取到 %d 个仓库" % count)
    # 示例：获取 openEuler 24.03-LTS-SP2 x86_64 架构的所有包（迭代打印前 10 个）
    # pkg_generator = oe.get_openEuler_everything_pkgs(
    #     os_version="24.03-LTS-SP1",
    #     os_arch="x86_64"
    # )
    # count=0
    # for name in pkg_generator:
    #     count+=1
    #     print(f"{name}")
    # print("共获取到 %d 个软件包" % count)
    pass

