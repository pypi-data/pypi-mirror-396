import os
from pathlib import Path

class B_Run_Maker:
    def __init__(self, run_dir_path='./runs'):
        self.run_dir_path: Path = Path(run_dir_path)
        os.makedirs(self.run_dir_path, exist_ok=True)

    def __get_count(self):
        # 统计self.run_dir_path下的文件夹数
        dirs = [1 for item in self.run_dir_path.iterdir() if item.is_dir()]
        count = sum(dirs)
        return count
    def make_dir(self) -> tuple[Path, str]:
        '''
        :return: dir_path, dirname
        '''
        count = self.__get_count()
        dir_path = self.run_dir_path / f'{count+1}'
        os.makedirs(dir_path, exist_ok=True)
        return dir_path, dir_path.name

if __name__ == '__main__':
    a = B_Run_Maker()
    a.make_dir()