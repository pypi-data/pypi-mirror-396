# 耐破損ファイル保存 [atomic_save]

import os
import sys
import slim_id

class Atomic_Save:
	# atomicに保存 [atomic_save]
	def __setitem__(self, path, data):
		# 型判定
		if type(data) == type(""):
			data = data.encode("utf-8")	# 文字列はバイト列として書き込む
		elif type(data) == type(b""):
			pass	# バイト列はそのまま書き込む
		else:
			raise Exception("[atomic_save error] The data to write must be a string or bytes.")
		# 一時ファイルパスの生成
		temp_id = slim_id.gen(lambda e: False, length = 6, ab = "16")
		temp_path = f"{path}.{temp_id}.atomic_save_temp"
		# 書き込み
		with open(temp_path, "wb") as f:
			# 一時ファイルにデータを書き込み
			f.write(data)
			# pythonとOSのバッファにあるデータをディスクに確実に書き込み
			f.flush()
			os.fsync(f.fileno())
		# ファイルの書き換え (アトミック)
		os.replace(temp_path, path)

# Atomic_Saveクラスのオブジェクトとモジュールを同一視
sys.modules[__name__] = Atomic_Save()
