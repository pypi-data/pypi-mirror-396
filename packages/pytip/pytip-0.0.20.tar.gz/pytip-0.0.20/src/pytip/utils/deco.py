from .base import *


# 실행 시간을 측정
def elapsed_time(function):
    @wraps(function)
    def wrapper(*args, **kwargs):

        start = time.time()
        result = function(*args, **kwargs)

        time_check = time.time() - start
        minute, second = divmod(time_check, 60)
        minute = int(minute)
        second = round(second, 2)
        if minute == 0:
            print(f"{function.__name__} : {second} sec")
        else:
            print(f"{function.__name__} : {minute} min {second} sec")

        return result
    return wrapper


# 웹 크롤링 실패시 반복실행
def web_retries(number_retries = 3):

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            for _ in range(number_retries):
                try:
                    return function(*args, **kwargs)
                except TypeError:
                    break

                # RecursionError 오류방지 방법
                # https://help.acmicpc.net/judge/rte/RecursionError
                except Exception as e: # except gaierror as e:
                    print(termcolor.colored(e, 'red'))
                    time.sleep(0.8)
            return None
        return wrapper

    return decorator
