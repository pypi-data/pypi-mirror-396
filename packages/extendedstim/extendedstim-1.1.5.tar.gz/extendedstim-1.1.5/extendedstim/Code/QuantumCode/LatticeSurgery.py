import copy
import galois
import networkx as nx
import numpy as np
from extendedstim.Code.QuantumCode.MajoranaCSSCode import MajoranaCSSCode
from extendedstim.Code.QuantumCode.MajoranaCode import MajoranaCode
from extendedstim.Code.QuantumCode.MajoranaColorCode import MajoranaColorCode
from extendedstim.Code.QuantumCode.SubsystemCode import SubsystemCode
from extendedstim.Physics.MajoranaOperator import MajoranaOperator


class MajoranaLatticeSurgery:

    # %%  CHAPTER：----生成Majorana Lattice Surgery----
    def __init__(self,code_A:MajoranaCSSCode,index_A:int,code_B:MajoranaCSSCode|None=None,index_B:int|None=None)->None:
        """""
        构造用于测量joint logical observable的lattice surgery代码
        input.code_A：Majorana CSS Code
        input.index_A：code_A中的logical observable的索引
        input.code_B：Majorana CSS Code
        input.index_B：code_B中的logical observable的索引
        """""

        ##  初始化属性
        self.observable:None|MajoranaOperator=None  # 待测的joint logical observable
        self.fixed_stabilizers_A=[]  # code_A中修改的stabilizer
        self.fixed_stabilizers_B=[]  # code_B中修改的stabilizer
        self.irrelevant_stabilizers_A=[]  # code_A中与joint logical observable无关的stabilizer
        self.irrelevant_stabilizers_B=[]  # code_B中与joint logical observable无关的stabilizer
        self.unfixed_stabilizers_A=[]  # code_A中还未修改的stabilizer
        self.unfixed_stabilizers_B=[]  # code_B中还未修改的stabilizer
        self.prime_stabilizers_A=[]  # code_A中z型stabilizer
        self.prime_stabilizers_B=[]  # code_B中z型stabilizer
        self.gauge_stabilizers=[]  # lattice surgery生成的gauge stabilizers
        self.measurement_stabilizers=[]  # lattice surgery生成的measurement stabilizers
        self.graph=None  # lattice surgery过程中的graph
        self.ancilla_number=0  # lattice surgery过程中生成的ancilla sites数目

        ##  根据输入的情况不同使用两种不同的lattice surgery method
        if index_B is None or code_B is None:
            self.code_A=code_A
            self.index_A=index_A
            self._ZechuanLatticeSurgery()
        else:
            if code_A.logical_operators_x[index_A].weight>code_B.logical_operators_x[index_B].weight:
                self.code_A=code_A
                self.code_B=code_B
                self.index_A=index_A
                self.index_B=index_B
            else:
                self.code_A=code_B
                self.code_B=code_A
                self.index_A=index_B
                self.index_B=index_A

            self._MajoranaLatticeSurgery()

        self.physical_number=code_A.physical_number+self.code_B.physical_number+self.ancilla_number
        self.ancilla_stabilizers=[MajoranaOperator([code_A.physical_number+self.code_B.physical_number+temp],[code_A.physical_number+code_B.physical_number+temp],1j) for temp in range(self.ancilla_number)]
        self.code=MajoranaCode(self.irrelevant_stabilizers_A+self.irrelevant_stabilizers_B+self.prime_stabilizers_A+self.prime_stabilizers_B+
                                     self.fixed_stabilizers_A+self.fixed_stabilizers_B+self.gauge_stabilizers,
                                     code_A.physical_number+self.code_B.physical_number+self.ancilla_number)
        subsystem_code_temp=SubsystemCode(self.code,self.ancilla_stabilizers+self.measurement_stabilizers+self.unfixed_stabilizers_A+self.unfixed_stabilizers_B)

        ##  从logical operators取出反对易于可观测量的算符
        anticommute=None
        for i in range(len(subsystem_code_temp.logical_operators)):
            if not MajoranaOperator.commute(self.observable,subsystem_code_temp.logical_operators[i]):
                anticommute=subsystem_code_temp.logical_operators[i]
        if anticommute is None:
            raise ValueError("The observable does not commute with any stabilizer.")

        ##  生成subsystem code
        self.subsystem_code=SubsystemCode(self.code,self.ancilla_stabilizers+self.measurement_stabilizers+self.unfixed_stabilizers_A+self.unfixed_stabilizers_B+[anticommute])

    # %%  CHAPTER：实现fermionic lattice surgery, method 1
    def _MajoranaLatticeSurgery(self):
        code_A:MajoranaCSSCode=self.code_A.copy()
        code_B:MajoranaCSSCode=self.code_B.copy()
        assert isinstance(code_A, MajoranaCSSCode)
        assert isinstance(code_B, MajoranaCSSCode)
        assert isinstance(self.index_A, int)
        assert isinstance(self.index_B, int)

        # %%  SECTION：----数据预处理----
        majorana_number_A=code_A.physical_number
        majorana_number_B=code_B.physical_number
        logical_operator_A=code_A.logical_operators_x[self.index_A]
        logical_operator_B=code_B.logical_operators_x[self.index_B]
        logical_operator_B.occupy_x=logical_operator_B.occupy_x+majorana_number_A
        self.observable=1j*logical_operator_A@logical_operator_B
        code_A.index_map(np.arange(majorana_number_A),majorana_number_A+majorana_number_B)
        code_B.index_map(np.arange(majorana_number_A, majorana_number_A+majorana_number_B),majorana_number_A+majorana_number_B)

        unfixed_stabilizers_A= [temp for temp in code_A.generators if len(set(temp.occupy_x) & set(logical_operator_A.occupy_x)) > 0]
        unfixed_stabilizers_B= [temp for temp in code_B.generators if len(set(temp.occupy_x) & set(logical_operator_B.occupy_x)) > 0]
        self.unfixed_stabilizers_A=copy.deepcopy(unfixed_stabilizers_A)
        self.unfixed_stabilizers_B=copy.deepcopy(unfixed_stabilizers_B)
        irrelevant_stabilizers_A= [temp for temp in code_A.generators if len(set(temp.occupy_x) & set(logical_operator_A.occupy_x)) == 0 and len(temp.occupy_x)>0]
        irrelevant_stabilizers_B= [temp for temp in code_B.generators if len(set(temp.occupy_x) & set(logical_operator_B.occupy_x)) == 0 and len(temp.occupy_x)>0]
        prime_stabilizers_A= [temp for temp in code_A.generators if len(temp.occupy_x)==0]
        prime_stabilizers_B= [temp for temp in code_B.generators if len(temp.occupy_x)==0]
        self.irrelevant_stabilizers_A=irrelevant_stabilizers_A
        self.irrelevant_stabilizers_B=irrelevant_stabilizers_B
        self.prime_stabilizers_A=prime_stabilizers_A
        self.prime_stabilizers_B=prime_stabilizers_B
        ancilla_mode_number=0

        ##  为待修改的stabilizers增加ancilla及其索引
        for i in range(len(unfixed_stabilizers_A)):

            ##  当前stabilizer需要增加的ancilla sites数目
            result_temp = [ancilla_mode_number+temp for temp in range(len(set(unfixed_stabilizers_A[i].occupy_x)&set(logical_operator_A.occupy_x)))]
            self.fixed_stabilizers_A.append((unfixed_stabilizers_A[i].copy(), result_temp))
            ancilla_mode_number+=len(result_temp)

        for i in range(len(unfixed_stabilizers_B)):

            ##  当前stabilizer需要增加的ancilla sites数目
            result_temp=[ancilla_mode_number+temp for temp in range(len(set(unfixed_stabilizers_B[i].occupy_x)&set(logical_operator_B.occupy_x)))]
            self.fixed_stabilizers_B.append((unfixed_stabilizers_B[i].copy(), result_temp))
            ancilla_mode_number+=len(result_temp)

        # %%  SECTION：加入测量稳定子，总是假设左边更长
        ##  先将两边对齐的部分连起来
        for i in range(len(logical_operator_B.occupy_x)):
            self.measurement_stabilizers.append(([logical_operator_A.occupy_x[i],logical_operator_B.occupy_x[i]],[]))
        for i in range((len(logical_operator_A.occupy_x)-len(logical_operator_B.occupy_x))//2):
            self.measurement_stabilizers.append(([logical_operator_A.occupy_x[2*i+len(logical_operator_B.occupy_x)],logical_operator_A.occupy_x[2*i+len(logical_operator_B.occupy_x)+1]],[]))

        ##  分析fixed stabilizers与measurement的交叉情况加入ancilla
        for i in range(len(self.fixed_stabilizers_A)):
            flag_temp=0
            for j in range(len(self.measurement_stabilizers)):
                number=len(set(self.fixed_stabilizers_A[i][0].occupy_x)&set(self.measurement_stabilizers[j][0]))
                for k in range(number):
                    self.measurement_stabilizers[j][1].append(self.fixed_stabilizers_A[i][1][flag_temp+k])
                flag_temp+=number

        for i in range(len(self.fixed_stabilizers_B)):
            flag_temp=0
            for j in range(len(self.measurement_stabilizers)):
                number=len(set(self.fixed_stabilizers_B[i][0].occupy_x)&set(self.measurement_stabilizers[j][0]))
                for k in range(number):
                    self.measurement_stabilizers[j][1].append(self.fixed_stabilizers_B[i][1][flag_temp+k])
                flag_temp+=number

        ##  处理odd-weight measurement stabilizers
        for i in range(len(self.measurement_stabilizers)):
            if len(self.measurement_stabilizers[i][1])%2!=0:
                self.measurement_stabilizers[i][1].append(ancilla_mode_number)
                ancilla_mode_number+=1

        # %%  SECTION：图论计算规范稳定子
        mode_vertices=['Mode'+str(temp) for temp in range(ancilla_mode_number)]
        fix_A_vertices=[]
        fix_B_vertices=[]
        measurement_vertices=[]
        edges=[]
        for i in range(len(self.fixed_stabilizers_A)):
            fix_A_vertices.append('FixA'+str(i))
            for j in range(len(self.fixed_stabilizers_A[i][1])):
                edges.append(('FixA'+str(i), 'Mode'+str(self.fixed_stabilizers_A[i][1][j])))
        for i in range(len(self.fixed_stabilizers_B)):
            fix_B_vertices.append('FixB'+str(i))
            for j in range(len(self.fixed_stabilizers_B[i][1])):
                edges.append(('FixB'+str(i), 'Mode'+str(self.fixed_stabilizers_B[i][1][j])))
        for i in range(len(self.measurement_stabilizers)):
            measurement_vertices.append('Measure'+str(i))
            for j in range(len(self.measurement_stabilizers[i][1])):
                edges.append(('Measure'+str(i), 'Mode'+str(self.measurement_stabilizers[i][1][j])))

        graph = nx.Graph()
        graph.add_nodes_from(mode_vertices)
        graph.add_nodes_from(fix_A_vertices)
        graph.add_nodes_from(fix_B_vertices)
        graph.add_nodes_from(measurement_vertices)
        graph.add_edges_from(edges)
        qubit_list=[]
        check_list=[]
        for index, value in enumerate(graph.nodes()):
            if 'FixA' in value or 'FixB' in value or 'Measure' in value:
                check_list.append(value)
            else:
                qubit_list.append(value)
        matrix=np.zeros((len(check_list), len(qubit_list)), dtype=int)
        for index0, check in enumerate(check_list):
            for index1, qubit in enumerate(qubit_list):
                if (qubit, check) in graph.edges():
                    matrix[index0, index1]=1
        GF=galois.GF(2**1)
        matrix=GF(matrix)
        result=matrix.null_space()
        check_gauge_list=[]
        for i in range(len(result)):
            index_list=np.where(result[i]!=0)[0]
            check_gauge_list.append(index_list)

        temp_list=[]
        for i in range(len(self.fixed_stabilizers_A)):
            occupy_x_temp=self.fixed_stabilizers_A[i][0].occupy_x.tolist()+[temp//2+majorana_number_A+majorana_number_B for temp in self.fixed_stabilizers_A[i][1] if temp%2==0]
            occupy_z_temp=self.fixed_stabilizers_A[i][0].occupy_z.tolist()+[(temp-1)//2+majorana_number_A+majorana_number_B for temp in self.fixed_stabilizers_A[i][1] if temp%2==1]
            temp_list.append(MajoranaOperator.HermitianOperatorFromOccupy(occupy_x_temp,occupy_z_temp))
        self.fixed_stabilizers_A=temp_list
        temp_list=[]
        for i in range(len(self.fixed_stabilizers_B)):
            occupy_x_temp=self.fixed_stabilizers_B[i][0].occupy_x.tolist()+[temp//2+majorana_number_A+majorana_number_B for temp in self.fixed_stabilizers_B[i][1] if temp%2==0]
            occupy_z_temp=self.fixed_stabilizers_B[i][0].occupy_z.tolist()+[(temp-1)//2+majorana_number_A+majorana_number_B for temp in self.fixed_stabilizers_B[i][1] if temp%2==1]
            temp_list.append(MajoranaOperator.HermitianOperatorFromOccupy(occupy_x_temp,occupy_z_temp))
        self.fixed_stabilizers_B=temp_list
        temp_list=[]
        for i in range(len(self.measurement_stabilizers)):
            occupy_x_temp=self.measurement_stabilizers[i][0]+[temp//2+majorana_number_A+majorana_number_B for temp in self.measurement_stabilizers[i][1] if temp%2==0]
            occupy_z_temp=[(temp-1)//2+majorana_number_A+majorana_number_B for temp in self.measurement_stabilizers[i][1] if temp%2==1]
            temp_list.append(MajoranaOperator.HermitianOperatorFromOccupy(occupy_x_temp,occupy_z_temp))
        self.measurement_stabilizers=temp_list
        temp_list=[]
        for i in range(len(check_gauge_list)):
            occupy_x_temp=[temp//2+majorana_number_A+majorana_number_B for temp in check_gauge_list[i] if temp%2==0]
            occupy_z_temp=[(temp-1)//2+majorana_number_A+majorana_number_B for temp in check_gauge_list[i] if temp%2==1]
            temp_list.append(MajoranaOperator.HermitianOperatorFromOccupy(occupy_x_temp,occupy_z_temp))
        self.gauge_stabilizers=temp_list
        self.graph=graph
        self.ancilla_number=ancilla_mode_number//2

    #%%  CHAPTER：Zechuan Lattice Surgery
    def _ZechuanLatticeSurgery(self):

        #%%  SECTION：----数据标准化----
        code_A: MajoranaCSSCode=self.code_A.copy()
        code_B: MajoranaColorCode=MajoranaColorCode(code_A.logical_operators_x[self.index_A].weight)
        self.code_B=code_B.copy()
        self.index_B=0
        majorana_number_A=code_A.physical_number
        majorana_number_B=code_B.physical_number
        logical_operator_A=code_A.logical_operators_x[self.index_A]
        logical_operator_B=code_B.logical_operators_x[0]
        logical_operator_B.occupy_x=logical_operator_B.occupy_x+majorana_number_A
        self.observable=1j*logical_operator_A@logical_operator_B
        code_A.index_map(np.arange(majorana_number_A),majorana_number_A+majorana_number_B)
        code_B.index_map(np.arange(majorana_number_A, majorana_number_A+majorana_number_B),majorana_number_A+majorana_number_B)

        unfixed_stabilizers_A= [temp for temp in code_A.generators if len(set(temp.occupy_x) & set(logical_operator_A.occupy_x)) > 0]
        unfixed_stabilizers_B= [temp for temp in code_B.generators if len(set(temp.occupy_x) & set(logical_operator_B.occupy_x)) > 0]
        self.unfixed_stabilizers_A=copy.deepcopy(unfixed_stabilizers_A)
        self.unfixed_stabilizers_B=copy.deepcopy(unfixed_stabilizers_B)
        irrelevant_stabilizers_A= [temp for temp in code_A.generators if len(set(temp.occupy_x) & set(logical_operator_A.occupy_x)) == 0 and len(temp.occupy_x)>0]
        irrelevant_stabilizers_B= [temp for temp in code_B.generators if len(set(temp.occupy_x) & set(logical_operator_B.occupy_x)) == 0 and len(temp.occupy_x)>0]
        prime_stabilizers_A= [temp for temp in code_A.generators if len(temp.occupy_x)==0]
        prime_stabilizers_B= [temp for temp in code_B.generators if len(temp.occupy_x)==0]
        self.irrelevant_stabilizers_A=irrelevant_stabilizers_A
        self.irrelevant_stabilizers_B=irrelevant_stabilizers_B
        self.prime_stabilizers_A=prime_stabilizers_A
        self.prime_stabilizers_B=prime_stabilizers_B
        ancilla_mode_number=0
        edge_site_bin_A:list[list[int]]=[[] for _ in range(code_B.d)]
        edge_site_bin_B:list[list[int]]=[[] for _ in range(code_B.d)]
        used_flags=[False for _ in range(len(code_B.edge_stabilizers))]

        ##  为待修改的stabilizers增加ancilla及其索引
        for i in range(len(unfixed_stabilizers_A)):
            overlaps=list(set(unfixed_stabilizers_A[i].occupy_x)&set(logical_operator_A.occupy_x))
            for j in range(len(overlaps)//2):
                index_0=int(np.where(logical_operator_A.occupy_x==overlaps[2*j])[0][0])
                index_1=int(np.where(logical_operator_A.occupy_x==overlaps[2*j+1])[0][0])
                edge_site_bin_A[index_0].append(ancilla_mode_number)
                edge_site_bin_A[index_1].append(ancilla_mode_number+1)
                self.fixed_stabilizers_A.append((unfixed_stabilizers_A[i].copy(), [ancilla_mode_number,ancilla_mode_number+1]))
                edge_site_bin_B[index_0].append(ancilla_mode_number+2)
                edge_site_bin_B[index_1].append(ancilla_mode_number+3)
                self.fixed_stabilizers_B.append((code_B.get_between(index_0,index_1), [ancilla_mode_number+2, ancilla_mode_number+3]))
                small=min(index_0,index_1)
                big=max(index_0,index_1)
                used_flags[small]=True
                used_flags[big-1]=True
                self.gauge_stabilizers.append([ancilla_mode_number+temp for temp in range(4)])
                ancilla_mode_number+=4

        ##  处理落单的edge stabilizers
        for i in range(len(used_flags)):
            if not used_flags[i]:
                edge_site_bin_B[i].append(ancilla_mode_number)
                edge_site_bin_B[i].append(ancilla_mode_number+1)
                edge_site_bin_B[i+1].append(ancilla_mode_number+2)
                edge_site_bin_B[i+1].append(ancilla_mode_number+3)
                self.fixed_stabilizers_B.append((code_B.get_between(i,i+1), [ancilla_mode_number, ancilla_mode_number+2]))
                self.gauge_stabilizers.append([ancilla_mode_number+temp for temp in range(4)])
                ancilla_mode_number+=4

        ##  添加measurement stabilizers
        for i in range(len(edge_site_bin_A)):
            self.measurement_stabilizers.append(([logical_operator_A.occupy_x[i], logical_operator_B.occupy_x[i]],edge_site_bin_A[i]+edge_site_bin_B[i]))

        temp_list=[]
        for i in range(len(self.fixed_stabilizers_A)):
            occupy_x_temp=self.fixed_stabilizers_A[i][0].occupy_x.tolist()+[temp//2+majorana_number_A+majorana_number_B for temp in self.fixed_stabilizers_A[i][1] if temp%2==0]
            occupy_z_temp=self.fixed_stabilizers_A[i][0].occupy_z.tolist()+[(temp-1)//2+majorana_number_A+majorana_number_B for temp in self.fixed_stabilizers_A[i][1] if temp%2==1]
            temp_list.append(MajoranaOperator.HermitianOperatorFromOccupy(occupy_x_temp,occupy_z_temp))
        self.fixed_stabilizers_A=temp_list
        temp_list=[]
        for i in range(len(self.fixed_stabilizers_B)):
            occupy_x_temp=self.fixed_stabilizers_B[i][0].occupy_x.tolist()+[temp//2+majorana_number_A+majorana_number_B for temp in self.fixed_stabilizers_B[i][1] if temp%2==0]
            occupy_z_temp=self.fixed_stabilizers_B[i][0].occupy_z.tolist()+[(temp-1)//2+majorana_number_A+majorana_number_B for temp in self.fixed_stabilizers_B[i][1] if temp%2==1]
            temp_list.append(MajoranaOperator.HermitianOperatorFromOccupy(occupy_x_temp,occupy_z_temp))
        self.fixed_stabilizers_B=temp_list
        temp_list=[]
        for i in range(len(self.measurement_stabilizers)):
            occupy_x_temp=self.measurement_stabilizers[i][0]+[temp//2+majorana_number_A+majorana_number_B for temp in self.measurement_stabilizers[i][1] if temp%2==0]
            occupy_z_temp=[(temp-1)//2+majorana_number_A+majorana_number_B for temp in self.measurement_stabilizers[i][1] if temp%2==1]
            temp_list.append(MajoranaOperator.HermitianOperatorFromOccupy(occupy_x_temp,occupy_z_temp))
        self.measurement_stabilizers=temp_list
        temp_list=[]
        for i in range(len(self.gauge_stabilizers)):
            occupy_x_temp=[temp//2+majorana_number_A+majorana_number_B for temp in self.gauge_stabilizers[i] if temp%2==0]
            occupy_z_temp=[(temp-1)//2+majorana_number_A+majorana_number_B for temp in self.gauge_stabilizers[i] if temp%2==1]
            temp_list.append(MajoranaOperator.HermitianOperatorFromOccupy(occupy_x_temp,occupy_z_temp))

        self.gauge_stabilizers=temp_list
        self.ancilla_number=ancilla_mode_number//2