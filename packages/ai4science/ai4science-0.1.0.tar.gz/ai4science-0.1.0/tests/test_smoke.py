"""
@Project  : ai4science
@File     : test_smoke.py
@Author   : Shaobo Cui
@Date     : 12.12.2025 11:56
"""


from ai4science import hello

def test_hello():
    assert "ai4science" in hello().lower()
