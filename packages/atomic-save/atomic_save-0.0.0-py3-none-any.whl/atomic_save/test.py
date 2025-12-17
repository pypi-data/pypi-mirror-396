# 耐破損ファイル保存 [atomic_save]
# 【動作確認 / 使用例】

import sys
import ezpip
atomic_save = ezpip.load_develop("atomic_save", "../", develop_flag = True)

# atomicに保存 [atomic_save]
atomic_save["./testfile.txt"] = "hello!"

# atomicに保存 [atomic_save]
atomic_save["./testfile.txt"] = b"hello!"
