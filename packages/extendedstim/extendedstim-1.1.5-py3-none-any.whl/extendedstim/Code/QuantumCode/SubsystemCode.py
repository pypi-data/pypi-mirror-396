from extendedstim.Code.QuantumCode.MajoranaCode import MajoranaCode
from extendedstim.Code.QuantumCode.PauliCode import PauliCode
from extendedstim.Physics.MajoranaOperator import MajoranaOperator
from extendedstim.Physics.PauliOperator import PauliOperator
from extendedstim.tools.GaloisTools import minus, distance


class SubsystemCode:
    def __init__(self,code:MajoranaCode|PauliCode,gauges):
        """""
        input.code：MajoranaCode 或 PauliCode 实例
        input.gauges：MajoranaOperator 或 PauliOperator 列表，作为码面上的测量算子
        output：无
        """""
        self.code=code
        self.gauges=gauges
        if isinstance(code,MajoranaCode):
            self.code_type=MajoranaCode
            self.operator_type=MajoranaOperator
        elif isinstance(code,PauliCode):
            self.code_type=PauliCode
            self.operator_type=PauliOperator
        else:
            raise ValueError("code must be MajoranaCode or PauliCode")

    @property
    def logical_operators(self)->list[MajoranaOperator|PauliOperator]:
        """""
        output：list[MajoranaOperator|PauliOperator]，独立逻辑算符集合
        """""
        result=self.code.logical_operators
        result=self.operator_type.get_matrix(result,self.code.physical_number)
        result=minus(result,self.operator_type.get_matrix(self.gauges,self.code.physical_number))
        results=[]
        for i in range(len(result)):
            results.append(self.operator_type.HermitianOperatorFromVector(result[i]))
        return results

    @property
    def distance(self)->int:
        """""
        output：int，码距
        """""
        return distance(self.code.check_matrix,self.operator_type.get_matrix(self.gauges,self.code.physical_number),'mip')