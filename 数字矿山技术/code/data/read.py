import pickle
import io
import pprint

# 超强屏蔽缺失模块，彻底解决 KeyError: 'data'
class MockUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except:
            # 找不到的模块/类全部返回空对象，不报错
            return type('Mock', (), {})

# 读取文件
with open("pt3_data.pkl", "rb") as f:
    unpickler = MockUnpickler(f)
    data = unpickler.load()

# 直接打印内容
print("="*40)
print("📂 pkl 文件内容：")
print("="*40)
pprint.pprint(data)

print("\n✅ 读取成功！")