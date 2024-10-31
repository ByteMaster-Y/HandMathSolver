import math
import re

# 손글씨 연산
def calculate_sqrt(expression):
    # 정규 표현식을 사용하여 루트 기호와 숫자를 찾습니다.
    while '√' in expression:
        # Python의 re 모듈에서 제공하는 함수로, 주어진 문자열(expression)에서 정규 표현식에 일치하는 첫 번째 부분을 찾는다. 
        # 찾으면 매치 객체를 반환하고, 없으면 None을 반환합니다.
        match = re.search(r'√(\d+)', expression)
        if match:
            sqrt_buff = match.group(1)
            root = round(math.sqrt(float(sqrt_buff)), 2)  # 소수점 2자리로 반올림
            expression = expression.replace('√' + sqrt_buff, str(root))
    return expression

def calculate_operation(operation):
    def precedence(op):
        if op == 'x':
            return 2
        elif op in ('+', '-'):
            return 1
        return 0

    def apply_op(values, ops, steps):
        if len(values) < 2:
            return  # 리스트에 충분한 값이 없으면 함수 종료

        right = values.pop()
        left = values.pop()
        op = ops.pop()
        if op == '+':
            result = left + right
        elif op == '-':
            result = left - right
        elif op == 'x':
            result = left * right
        values.append(round(result, 2))  # 소수점 2자리로 반올림
        # 각 단계의 계산 과정을 설명으로 추가
        if op == 'x':
            steps.append(f"{left} x {right}: 첫 번째로 {left} x {right}를 계산합니다. {left} 곱하기 {right}는 {result}입니다.")
        elif op == '-':
            steps.append(f"{left} - {right}: 그 다음으로, {left} - {right}를 계산합니다. {left}에서 {right}를 빼면 {result}가 됩니다.")
        elif op == '+':
            steps.append(f"{left} + {right}: 마지막으로 {left} + {right}를 계산합니다. {left}에서 {right}를 더하면 {result}가 됩니다.")

    values = []
    ops = []
    steps = []
    i = 0

    while i < len(operation):
        if operation[i].isdigit() or (operation[i] == '.' and i + 1 < len(operation) and operation[i + 1].isdigit()):
            val = ''
            while i < len(operation) and (operation[i].isdigit() or operation[i] == '.'):
                val += operation[i]
                i += 1
            values.append(round(float(val), 2))
            i -= 1
        elif operation[i] in '+x-':
            while ops and precedence(ops[-1]) >= precedence(operation[i]):
                apply_op(values, ops, steps)
            ops.append(operation[i])
        i += 1

    while ops:
        apply_op(values, ops, steps)

    # 최종 설명 생성
    explanation_steps = "<br>".join(steps)
    # explanation = f"{explanation_steps}<br>최종 {operation}을 연산한 결과는 [{values[-1]}]입니다."
    explanation = f"{explanation_steps}<br>최종 {operation}을 연산한 결과는 [{round(values[-1], 2)}]입니다."  # 최종 결과를 소수점 2자리로 반올림
    return values[-1], explanation


