CONSTANT_VALUE = 100
# ===== 示例函数定义 =====
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

def divide(a, b):
    return a / b

def calculate_sum(x, y, z=0, *args, **kwargs):
    """带有多种参数类型的示例函数"""
    total = x + y + z + sum(args)
    for key, value in kwargs.items():
        if isinstance(value, (int, float)):
            total += value
    return total

def fun1(x, y):
    return x + y 
def fun2(x, y):
    return fun1(x, y) + CONSTANT_VALUE

def main():
    print("开始计算阶乘")
    result = factorial(3)
    print(f"阶乘计算结果: {result}")
    
    print("\n测试多参数函数:")
    sum_result = calculate_sum(1, 2, 3, 4, 5, bonus=10, extra=20)
    print(f"求和结果: {sum_result}")
    
    print("\n测试异常处理:")
    try:
        result2 = divide(10, 0)
    except ZeroDivisionError as e:
        print(f"捕获异常: {e}")
    
    add_value = fun2(20, 3)
    print("")
if __name__ == "__main__":
# ===== 运行程序 =====
    main()  