import base64
import json
import os
from pathlib import Path
import shutil
import sys
import time
import urllib.request
from base.log import log_util


def Retry(func, times, *args, **kwargs):
    '''
    重试函数, 文件操作容易因资源竞争导致失败, 因此需要失败后重试
    '''
    for _ in range(times):
        value = func(*args, **kwargs)  
        if value:
            return value
        time.sleep(5)
    return False

class FileUtil:
    '''
    封装常用的文件操作工具, 方便快速完成文件操作
    '''
    logger = log_util.BccacheLogger(name="FileUtil")
    
    @classmethod
    def remove_folder(cls, folder: str, retry_times: int = 5) -> bool:
        def remove_folder_impl():
            if not os.path.exists(folder):
                cls.logger.info('[RemoveFolder]', folder, 'not existed')
                return True

            cls.logger.info('[RemoveFolder]', 'Delete', folder)
            try:
                shutil.rmtree(folder)
            except BaseException as e:
                cls.logger.error('[RemoveFolder]', e)

            ret = not os.path.exists(folder)
            cls.logger.info('[RemoveFolder]', 'Delete', folder,
                'success' if ret else 'failure')
            return ret

        Retry(remove_folder_impl, retry_times)
        
    @classmethod
    def remove_file(cls, file: str, retry_times: int = 5) -> bool:
        def remove_file_impl():
            try:
                if not os.path.exists(file):
                    cls.logger.info('[RemoveFile]', file, 'not existed')
                    return True

                cls.logger.info('[RemoveFile]', 'Delete', file)
                os.remove(file)
            except BaseException as e:
                cls.logger.error('[RemoveFile]', e)

            ret = not os.path.exists(file)
            cls.logger.info('[RemoveFile]', 'Delete', file, 'success' if ret else 'failure')
            return ret

        return Retry(remove_file_impl, retry_times)
    
    @classmethod
    def get_folder_size(cls, folder: str, details: dict = {}) -> int:
        '''
        计算指定目录的 size 大小, 一般会用来统计 out 缓存目录的大小, 做调试确认信息使用
        
        Agrs:
            folder: 目录路径名
            details: 可选参数, 用于收集目录中每个文件和子目录的详细大小信息
            
        Returns:
            返回整个目录的总体积
        '''
        if folder is None:
            return 0

        if not os.path.exists(folder):
            return 0

        size = 0
        for r in os.listdir(folder):
            item = os.path.join(folder, r)

            if os.path.islink(item) or os.path.isfile(item):
                item_size = os.path.getsize(item)
                # 链接符号不计算大小, 主要是两层考虑
                # 1. 链接文件指向的实体若不在 folder 下, 则不应该计算大小
                # 2. 链接文件指向的实体若在 folder 下, 则会重复计算大小
                # 但需要将 folder 的所有文件记录添加至 details 中
                if os.path.islink(item):
                    item_size = 0
                if details is not None:
                    details[r] = item_size
                size += item_size

            elif os.path.isdir(item):
                temp_tails = {}
                size += cls.FolderSize(item, temp_tails)
                if details is not None:
                    details[r] = temp_tails

        return size
    
    @classmethod
    def make_directory_exists(cls, dirname: str) -> bool:
        if dirname is None or dirname == '':
            return False

        cls.logger.info(f"[make] Make {dirname} existed")
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return True
    
    @classmethod
    def download_url(cls, url: str, local_path: str) -> bool:
        cls.logger.info(f"download {url} => {local_path}")
        def DownloadURL_Impl():
            try:
                if os.path.dirname(local_path) != '':
                    if not os.path.exists(os.path.dirname(local_path)):
                        cls.make_directory_exists(os.path.dirname(local_path))
                urllib.request.urlretrieve(url, local_path)
                return True
            except BaseException as e:
                cls.logger.error(f"[download] error: {e}")
                return False
        if not Retry(DownloadURL_Impl, 50):
            cls.logger.error(f"Fail to download {url}")
            return False
        return True
        
    @classmethod
    def send_http_post_request(cls, post_url, content, method='POST',
                authorization=None, get_header=False,
                allow_exceptions=False, custom_header=None, asw=None):
        '''
        Args:
            allow_exceptions: 为 True 代表不重试任务直接失败, 否则会重试 post 任务
            asw: 为 True 可以获取接口返回的报错信息 例如401 或者 404 等错误码 直接返回错误码 不重试任务直接失败
        '''
        def HttpPost_Impl():
            try:
                header = {
                    "Content-Type": "application/json; charset=utf-8",
                    "accept": "application/json, text/plain, */*",
                }
                if custom_header is not None:
                    header.update(custom_header)
                if authorization is not None:
                    if authorization.startswith('Bearer'):
                        header['Authorization'] = authorization
                    else:
                        if isinstance(authorization, str):
                            authorizations = authorization.encode('utf-8')
                            header['Authorization'] = 'Basic {}'.format(
                                base64.b64encode(authorizations).decode('ascii'))

                body = json.dumps(content).encode('utf-8')
                request = urllib.request.Request(post_url, data=body, headers=header)
                request.get_method = lambda: method
                try:
                    response = urllib.request.urlopen(request, timeout=30)
                except urllib.error.HTTPError as e:
                    response = e
                    cls.logger.error(response)
                if get_header:
                    res = json.dumps(dict(response.headers))
                else:
                    res = json.loads(response.read().decode('utf-8'))
                if len(res) == 0:
                    res = '{}'
                if not asw and "code" in res and not (res["code"] in [0, 1, 200, "0", "1", "200"]):
                    cls.logger.error(('[http] request fail method:', method))
                    cls.logger.error(('[http] request fail post_url:', post_url))
                    cls.logger.error(('[http] request fail data:', content))
                    cls.logger.error(("[http] request fail res:", res))
                return res
            except urllib.error.URLError as e:
                if allow_exceptions:
                    raise e

                cls.logger.error('[http]', e)
                if hasattr(e, 'code') and hasattr(e, 'read'):
                    cls.logger.error('[http]', e.code)
                    try:
                        res = e.read().decode('utf-8') if hasattr(e.read(), 'decode') else e.read()
                        cls.logger.info('[content]', res)
                    except Exception as ex:
                        cls.logger.error('[http] Failed to read error content:', ex)

                if asw is not None:
                    return e
                return False

        res = Retry(HttpPost_Impl, 5)
        if res is False:
            cls.logger.error('[http]', 'Fail to send http post request', post_url)
            sys.exit(1)
        return res
    
    @classmethod
    def find_all_symlinks(cls, path: str) -> list[Path]:
        """
        查找指定目录下所有软链接文件（含子目录）
        :param path: 目标目录路径（绝对/相对）
        :return: 所有软链接的 Path 对象列表
        """
        target_dir = Path(path).resolve()  # 解析为绝对路径，避免相对路径问题
        if not target_dir.is_dir():
            raise ValueError(f"路径 {path} 不是有效目录")
        
        # 递归遍历所有文件，筛选软链接
        symlinks = []
        # rglob("*") 匹配所有文件/目录，包括隐藏文件
        for file_path in target_dir.rglob("*"):
            # is_symlink() 判断是否为软链接（即使目标不存在也会返回 True）
            if file_path.is_symlink():
                symlinks.append(str(file_path))
        return symlinks
    
    @classmethod
    def get_relative_path(cls, absolute_path: str, relative_to_dir: str) -> str:
        """
        将绝对路径转换为相对于指定目录的相对路径
        如果绝对路径不是基准目录的子目录，则返回原始绝对路径
        
        Args:
            absolute_path: 要转换的绝对路径
            relative_to_dir: 相对的基准目录路径（绝对/相对均可）
            
        Returns:
            如果是子目录返回相对路径字符串，否则返回原始绝对路径
            
        Raises:
            ValueError: 当基准目录不存在时
        """
        try:
            # absolute() 仅转绝对路径，不解析软链接；resolve() 会解析软链接到真实路径
            abs_path = Path(absolute_path).absolute()
            rel_base_dir = Path(relative_to_dir).absolute()

            # 验证基准目录是否存在且是目录
            if not rel_base_dir.exists() or not rel_base_dir.is_dir():
                raise ValueError(f"基准目录 {relative_to_dir} 不存在或不是有效的目录")
            
            # 避免 startswith 导致的部分匹配问题（如 /home/user1 误判为 /home/user 的子目录）
            if abs_path.is_relative_to(rel_base_dir):
                # 用 pathlib 的 relative_to 替代 os.path.relpath，风格统一且跨平台
                relative_path = abs_path.relative_to(rel_base_dir)
                return str(relative_path)
            else:
                # 不是子目录，返回原始路径的绝对形式（保持路径格式统一）
                return str(abs_path)
        except Exception as e:
            cls.logger.error(f"[GetRelativePath] 处理失败: {e}")
            # 异常时返回原始路径的字符串形式，避免 Path 对象泄露
            return str(Path(absolute_path))
    
    @classmethod
    def read_file(cls, file_path: str, encoding: str = 'utf-8') -> str:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            encoding: 文件编码, 默认utf-8
            
        Returns:
            文件内容字符串, 如果读取失败返回空字符串
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            cls.logger.info(f'[ReadFile] 读取文件 {file_path} 成功')
            return content
        except BaseException as e:
            cls.logger.error(f'[ReadFile] 读取文件 {file_path} 失败: {e}')
            return ''
    
    @classmethod
    def append_to_file(cls, file_path: str, content: str, retry_times: int = 5, add_newline: bool = True) -> bool:
        """
        向文件尾部追加插入内容
        
        Args:
            file_path: 文件路径
            content: 要追加的内容
            retry_times: 重试次数, 默认5次
            add_newline: 是否自动添加换行符, 默认True
            
        Returns:
            追加成功返回True, 否则返回False
        """
        def append_to_file_impl():
            if not os.path.exists(file_path):
                # 创建文件的父目录
                parent_dir = os.path.dirname(file_path)
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                # 创建空文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    pass
            try:
                # 检查是否需要添加换行符，避免修改外部变量
                write_content = content
                if add_newline and write_content and not write_content.endswith('\n'):
                    write_content += '\n'
                cls.logger.info(f'[AppendToFile] 向文件 {file_path} 追加内容为: {write_content}')
                with open(file_path, 'a', encoding='utf-8') as f:
                        f.write(write_content)
                cls.logger.info(f'[AppendToFile] 向文件 {file_path} 追加内容成功')
                return True
            except BaseException as e:
                cls.logger.error(f'[AppendToFile] 向文件 {file_path} 追加内容失败: {e}')
                return False
        return Retry(append_to_file_impl, retry_times)
    
    @classmethod
    def ensure_p4ignore_contains(cls, p4ignore_path: str, compare_list: list[str]) -> list[str]:
        """
        在指定的 `.p4ignore` 文件中，确保传入的待比较列表条目存在；
        若不存在，则在文件尾部插入，并在插入前添加时间标记行。
        时间标记格式：`#YYYYMMDDHHMM`
        
        Args:
            p4ignore_path: `.p4ignore` 文件路径
            compare_list: 待比较的路径列表
        
        Returns:
            实际新增插入的条目列表（已去重、去空）
        """
        try:
            existing: set[str] = set()
            if os.path.exists(p4ignore_path):
                with open(p4ignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        s = line.strip()
                        if not s or s.startswith('#'):
                            continue
                        existing.add(s)

            normalized = [item.strip() for item in (compare_list or []) if isinstance(item, str) and item.strip()]
            # 去重并过滤已存在条目，保持原始顺序
            uniq_norm = list(dict.fromkeys(normalized))
            to_add = [item for item in uniq_norm if item not in existing]

            if to_add:
                stamp = time.strftime('%Y%m%d%H%M', time.localtime())
                content = '\n'.join([f'#{stamp}'] + to_add)
                ok = cls.append_to_file(p4ignore_path, content, add_newline=True)
                cls.logger.info(f"[P4Ignore] Append {to_add} to {p4ignore_path} {'success' if ok else 'failure'}")
                if not ok:
                    return []
            else:
                cls.logger.info(f"[P4Ignore] No new items to add for {p4ignore_path}")

            return to_add
        except BaseException as e:
            cls.logger.error(f"[P4Ignore] ensure_p4ignore_contains error: {e}")
            return []
    
class ChangeDirectory:

    def __init__(self, new_directory):
        self.new_directory = new_directory
        self.current_directory = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_directory)

    def __exit__(self, exc_type, exc_value, trace):
        os.chdir(self.current_directory)
