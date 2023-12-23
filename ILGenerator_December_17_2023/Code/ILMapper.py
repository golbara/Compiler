
# https://en.wikipedia.org/wiki/List_of_CIL_instructions
class ILMapper:
    def __init__(self):
        self.max_register_count = -1
        self.register_counter = -1
        self.stack = []
        self.il_codes = []
        self.global_variables = []
        self.label_counter = 0

    relational_operators = ['>=', '>', '==', '!=', '<', '<=', '&&', '||', ]
    arithmetic_operators = ['+', '-', '*', '/',]
    operators = ['\":=\"',
                 '>=', '>', '==', '!=', '<', '<=',
                '+', '-', '*', '/',
                '&&', '||',
                '!', '&', '|', '^',
                '>>', '<<',
                'if',
                '\"?:\"',
                'block',
                 # '\"then:\"',
                 # '\"else:\"',
                 ]


    def create_temp_reg(self):
        self.register_counter += 1
        self.max_register_count += 1
        return 'T' + str(self.register_counter)

    def create_new_label(self):
        self.label_counter += 1
        return 'Label' + str(self.label_counter)

    def get_current_reg(self):
        self.register_counter += 1
        self.max_register_count += 1
        return 'T' + str(self.register_counter)
    
    def free_temp_reg(self):
        self.register_counter -= 1

    def add_global_variable(self,item):
        if item in self.global_variables:
            return
        else:
            self.global_variables.append(item)

    def generate_intermediate_language(self, post_order_array, pre_order_array=None):
        length = len(post_order_array)
        i = 0
        while(i<length):
            item = post_order_array[i]
            if self.is_operator(item):
                self.il_codes.append(self.generate_il_based_on_operator(item))
            elif item == "for":
                i = self.forst(post_order_array,i) - 1
                print("done!")
            elif item == "while":
                i = self.whilest(post_order_array,i)
            elif(self.is_identifier(item) or item.isnumeric()):
                if self.is_identifier(item):
                    self.add_global_variable(item)
                self.stack.append(item)
            elif item=="if":
                condition_result = self.stack.pop()
                i = self.ifst(post_order_array,i,condition_result) -1
            i+=1
            # print("***************************8")
            # print(self.stack)

        result = ''
        for string in self.il_codes:
            if string is not None:
                result += string

        with open("output.il", "w") as my_file:
            my_file.write(self.get_msil_header(self.max_register_count))
            my_file.write(result)
            my_file.write(self.get_msil_footer())
        return result

    def my_IL_generator(self,post_order_array,index):
        while (post_order_array[index] != "block"):
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print(self.stack)
            item = post_order_array[index]
            if self.is_operator(item):
                self.il_codes.append(self.generate_il_based_on_operator(item))
            elif item == "if":
                condition_result = self.stack.pop()
                self.ifst(post_order_array, index, condition_result)
            elif (self.is_identifier(item) or item.isnumeric()):
                if self.is_identifier(item):
                    self.add_global_variable(item)
                self.stack.append(item)
            index += 1
        index +=1 # jump the "block" element in the array
        return  index
    def is_temp_reg(self, code):
        return str.startswith(code, "T")

    def is_operator(self, item):
        if item in self.operators:
            return True
        else:
            return False

    def is_identifier(self, item):
        if not self.is_operator(item) and (item[0].isalpha() and item.isalnum()):
            return True
        else:
            return False

    def generate_il_based_on_operator(self, item):
        if item == '\":=\"':
            second_operand = self.stack.pop()
            first_operand = self.stack.pop()
            return self.assignment(first_operand, second_operand)
        if item in self.arithmetic_operators:
            second_operand = self.stack.pop()
            first_operand = self.stack.pop()
            return self.arithmetic(first_operand, second_operand,item)
        if item in self.relational_operators:
            second_operand = self.stack.pop()
            first_operand = self.stack.pop()
            return self.relational(first_operand, second_operand, item)
        if item == '\"?:\"':
            second_operand = self.stack.pop()
            first_operand = self.stack.pop()
            condition = self.stack.pop()
            return self.ternary(condition,first_operand,second_operand)
        # if item == '\"then:\"':
        #     if_condition_result = self.stack.pop()
        #     return  self.ifst(if_condition_result)






    def get_msil_header(self,used_regs):
        result = (".assembly extern mscorlib {}\n"
                ".assembly output {}\n"
                ".module output.exe\n"
                ".class private auto ansi beforefieldinit ConsoleApp1.Program extends [mscorlib]System.Object\n"
                "{\n"
                ".method private hidebysig static void  Main(string[] args) cil managed\n"
                "{\n"
                ".entrypoint\n"
                ".maxstack  100\n")
        for i in range(used_regs+1):
            result += f".locals init ([{i}] int64 T{i})\n"

        for i in range(len(self.global_variables)):
            result += f".locals init ([{i+used_regs+1}] int64 {self.global_variables[i] })\n"
        if not 'output' in self.global_variables:
            result += f".locals init ([{len(self.global_variables)+used_regs+1}] int64 output)\n"


        result += ("nop\n"
                "///////////////////////// IL CODE\n")

        return result

    @staticmethod
    def get_msil_footer():
        return ("\n///////////////////////// IL CODE\n"
                "ldloca.s   output\n"
                "call       instance string [mscorlib]System.Int64::ToString()\n"
                "call       void [mscorlib]System.Console::WriteLine(string)\n"
                "nop\n"
                "ret\n"
                "} // end of method Program::Main\n"
                ".method public hidebysig specialname rtspecialname instance void  .ctor() cil managed\n"
                "{\n"
                ".maxstack  8\n"
                "ldarg.0\n"
                "call       instance void [mscorlib]System.Object::.ctor()\n"
                "nop\n"
                "ret\n"
                "} // end of method Program::.ctor\n"
                "} // end of class\n")

    def arithmetic(self, a, b,item):
        first_load_statement = None
        second_load_statement = None
        operator = 'add' if item=='+' else 'sub' if item=='-' else 'div' if item=='/' else 'mul'
        if self.is_identifier(a):
            first_load_statement = f"ldloc {a}\n"
            if self.is_temp_reg(a):
                self.free_temp_reg()
        else:
            first_load_statement = f"ldc.i8 {a}\n"
        if self.is_identifier(b):
            second_load_statement = f"ldloc {b}\n"
            if self.is_temp_reg(b):
                self.free_temp_reg()
        else:
            second_load_statement = f"ldc.i8 {b}\n"

        result_reg = self.create_temp_reg()
        self.stack.append(result_reg)
        return first_load_statement + second_load_statement + f"{operator}\n"+f"stloc {result_reg}\n"

    def assignment(self,first_operand, second_operand):
        if not self.is_identifier(first_operand):
            raise Exception
        if self.is_identifier(second_operand):
            load_statement = f"ldloc {second_operand}\n"
            if self.is_temp_reg(second_operand):
                self.free_temp_reg()
        else:
            load_statement = f"ldc.i8 {second_operand}\n"
        return load_statement+f"stloc {first_operand}\n"

    def relational(self, a, b, item):
        first_load_statement = None
        second_load_statement = None
        operator = 'and' if item == '&&' else 'or' if item == '||' else 'ceq' if item == '==' else 'cgt'
        if self.is_identifier(a):
            first_load_statement = f"ldloc {a}\n"
            if self.is_temp_reg(a):
                self.free_temp_reg()
        else:
            first_load_statement = f"ldc.i8 {a}\n"
        if self.is_identifier(b):
            second_load_statement = f"ldloc {b}\n"
            if self.is_temp_reg(b):
                self.free_temp_reg()
        else:
            second_load_statement = f"ldc.i8 {b}\n"

        result_reg = self.create_temp_reg()
        self.stack.append(result_reg)
        return first_load_statement + second_load_statement + f"{operator}\n" + f"stloc {result_reg}\n"

    def ternary(self, condition, a, b):
        first_load_statement = None
        second_load_statement = None
        if self.is_identifier(condition):
            condition_load_statement = f"ldloc {condition}\n"
            if self.is_temp_reg(condition):
                self.free_temp_reg()
        else:
            condition_load_statement = f"ldc.i8 {condition}\n"
        if self.is_identifier(a):
            first_load_statement = f"ldloc {a}\n"
            if self.is_temp_reg(a):
                self.free_temp_reg()
        else:
            first_load_statement = f"ldc.i8 {a}\n"
        if self.is_identifier(b):
            second_load_statement = f"ldloc {b}\n"
            if self.is_temp_reg(b):
                self.free_temp_reg()
        else:
            second_load_statement = f"ldc.i8 {b}\n"

        result_reg = self.create_temp_reg()
        self.stack.append(result_reg)
        true_start_label = self.create_new_label()
        false_start_label = self.create_new_label()
        false_end_label = self.create_new_label()

        return condition_load_statement+f"brtrue {true_start_label}\n"+f"br {false_start_label}\n"+f"{true_start_label+':'}\n"+first_load_statement +f"br {false_end_label} \n" +f"{false_start_label+':'}\n"+second_load_statement+f"{false_end_label+':'}\n"+ f"stloc {result_reg}\n"

    def ifst(self, post_order_array,index, condition_result):
        # load condition result
        self.il_codes.append(f"ldloc {condition_result}\n")
        # branch to then lable
        then_label = self.create_new_label()
        self.il_codes.append(f"brtrue {then_label}\n")
        # branch to else lable
        else_label = self.create_new_label()
        self.il_codes.append(f"br {else_label}\n")
        # start instructions related to 'then'
        self.il_codes.append(f"{then_label+':'}\n")
        index += 1  # index of the first instruction after "then:" lable
        index = self.my_IL_generator(post_order_array,index)
        if (post_order_array[index] == '\"else:\"'):
            # insert else lable into il_codes list
            self.il_codes.append(f"{else_label+':'}\n")
            index = self.my_IL_generator(post_order_array,index)
        return index

    def forst(self,post_order_array,index):
        # passing through the "for" lable
        index += 1
        # load  the start value
        self.il_codes.append(f"ldc.i8 {post_order_array[index]}\n")
        # store the start value in the ID
        index += 1
        id = post_order_array[index]
        self.il_codes.append(f"stloc {id}\n")
        # jump over the "to"
        index+=2
        # load the stop value
        self.il_codes.append(f"ldc.i8 {post_order_array[index]}\n")
        # store the stop value in a temp register
        upper_bound_reg = self.create_temp_reg()
        self.il_codes.append(f"stloc {upper_bound_reg}\n")
        # set lable for the forLoop body
        for_body_lable = self.create_new_label()
        # visit the next element (enter to the body)
        # print forLoop body lable
        self.il_codes.append(f"{for_body_lable+':'}\n")
        index +=1
        index = self.my_IL_generator(post_order_array,index)
        # add one to the counter (i = i +1)
        first_load_statement = f"ldloc {id}\n"
        second_load_statement = f"ldc.i8 1\n"
        self.il_codes.append(first_load_statement + second_load_statement + f"ADD\n"+f"stloc {id}\n")
        # check if we have meet the limit
        ## load the upper_bound
        self.il_codes.append(f"ldloc {upper_bound_reg}\n")
        ## compare with id (which is increased by one)
        self.il_codes.append(f"ldloc {id}\n"+"ceq\n")
        # save the result of comparison between i and upper_bound in a temp reg
        temp_reg = self.create_temp_reg()
        self.il_codes.append(f"stloc {temp_reg}\n")
        # branch to the forLoop lable if we have not still meet the upper_bound
        exit_label = self.create_new_label()
        self.il_codes.append(f"brtrue {exit_label}\n"+f"br {for_body_lable}\n"+f"{exit_label}:\n")
        return  index

    def whilest(self,post_order_array,index):
        # jump from the while
        index +=1
        # generate il for condition
        first = post_order_array[index]
        index +=1
        second = post_order_array[index]
        index += 1
        operator = post_order_array[index]
        condition_il = self.relational(first,second,operator)
        condition_result = self.stack[0]
        # # check the complying of condition
        # self.il_codes.append(f"ldloc {condition_result}\n")
        self.il_codes.append(condition_il)
        # set label for whilest
        while_body_label = self.create_new_label()
        # generate exit lable
        exitWhile_label = self.create_new_label()
        # branch or do not (while lable / exit lable)
        self.il_codes.append(f"brtrue {exitWhile_label}\n"+f"br {while_body_label}\n")
        self.il_codes.append(f"{while_body_label + ':'}\n")
        # while instructions
        index += 1 # jump the parent condition node
        index = self.my_IL_generator(post_order_array,index)
        self.il_codes.append(condition_il)
        self.il_codes.append(f"{exitWhile_label}:\n")
        return  index