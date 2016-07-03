class Syntax(object):
    def __repr__(self):
        return '<<{}>>'.format(self)


class Number(Syntax):
    def __init__(self, value):
        self.value = value

    @property
    def is_reducible(self):
        return False

    def __str__(self):
        return str(self.value)


class Boolean(Syntax):

    def __init__(self, value):
        self.value = value

    @property
    def is_reducible(self):
        return False

    def __str__(self):
        return str(self.value)


class Add(Syntax):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    @property
    def is_reducible(self):
        return True

    def reduce(self, environment):
        if self.left.is_reducible:
            return Add(self.left.reduce(environment), self.right)
        elif self.right.is_reducible:
            return Add(self.left, self.right.reduce(environment))
        else:
            return Number(self.left.value + self.right.value)

    def __str__(self):
        return '{} + {}'.format(self.left, self.right)


class Multiply(Syntax):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    @property
    def is_reducible(self):
        return True

    def reduce(self, environment):
        if self.left.is_reducible:
            return Multiply(self.left.reduce(environment), self.right)
        elif self.right.is_reducible:
            return Multiply(self.left, self.right.reduce(environment))
        else:
            return Number(self.left.value * self.right.value)

    def __str__(self):
        return '{} * {}'.format(self.left, self.right)


class LessThan(Syntax):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    @property
    def is_reducible(self):
        return True

    def reduce(self, environment):
        if self.left.is_reducible:
            return LessThan(self.left.reduce(environment), self.right)
        elif self.right.is_reducible:
            return LessThan(self.left, self.right.reduce(environment))
        else:
            return Boolean(self.left.value < self.right.value)


    def __str__(self):
        return '{} < {}'.format(self.left, self.right)


class Variable(Syntax):

    def __init__(self, name):
        self.name = name

    @property
    def is_reducible(self):
        return True

    def reduce(self, environment):
        return environment[self.name]

    def __str__(self):
        return self.name

        
class DoNothing(Syntax):

    def __str__(self):
        return 'do-nothing'

    @property
    def is_reducible(self):
        return False

    def __eq__(self, other_statement):
        return isinstance(other_statement, DoNothing)


class Assign(Syntax):

    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

    @property
    def is_reducible(self):
        return True

    def reduce(self, environment):
        if self.expression.is_reducible:
            return Assign(self.name, self.expression.reduce(environment)), environment
        else:
            new_environment = environment.copy()
            new_environment[self.name] = self.expression
            return DoNothing(), new_environment
            

    def __str__(self):
        return '{} = {}'.format(self.name, self.expression)


class If(Syntax):

    def __init__(self, condition, consequence, alternative):
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    @property
    def is_reducible(self):
        return True

    def reduce(self, environment):
        if self.condition.is_reducible:
            return If(self.condition.reduce(environment), self.consequence, self.alternative), environment
        elif self.condition.value == True:
            return self.consequence, environment
        else:
            return self.alternative, environment

    def __str__(self):
        return 'if ({}){{ {} else {{ {} }}'.format(self.condition, self.consequence, self.alternative)


class Sequence(Syntax):

    def __init__(self, first_statement, second_statement):
        self.first_statement = first_statement
        self.second_statement = second_statement

    @property
    def is_reducible(self):
        return True

    def reduce(self, environment):
        if isinstance(self.first_statement, DoNothing):
            return self.second_statement, environment
        else:
            reduced_first, new_env = self.first_statement.reduce(environment)
            return Sequence(reduced_first, self.second_statement), new_env

    def __str__(self):
        return '{}; {}'.format(self.first_statement, self.second_statement)


class While(Syntax):

    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    @property
    def is_reducible(self):
        return True

    def reduce(self, environment):
        return If(self.condition, Sequence(self.body, self), DoNothing()), environment

    def __str__(self):
        return 'while ({}){{{}}}'.format(self.condition, self.body)


class Machine(object):
    def __init__(self, statement, environment):
        self.statement = statement
        self.environment = environment

    def run(self):
        while self.statement.is_reducible:
            print '{}     {}'.format(self.statement, self.environment)
            self.step()
        print '{}     {}'.format(self.statement, self.environment)

    def step(self):
        self.statement, self.environment = self.statement.reduce(self.environment)


if __name__ == '__main__':
    # statement = Assign('x', Add(Variable('x'), Number(1)))
    # environment = {'x': Number(2)}

    # machine = Machine(statement, environment)
    # print machine.run()

    # if_statement = If(
    #     Variable('x'),
    #     Assign('y', Number(1)),
    #     Assign('y', Number(2)),
    # )
    # environment = {'x': Boolean(True)}

    # machine = Machine(if_statement, environment)
    # print machine.run()



    # sequence_statement = Sequence(
    #     Assign('x', Add(Number(1), Number(1))),
    #     Assign('y', Add(Variable('x'), Number(3))),
    # )
    # environment = {}

    # machine = Machine(sequence_statement, environment)
    # print machine.run()


    while_statement = While(
        LessThan(Variable('x'), Number(5)),
        Assign('x', Multiply(Variable('x'), Number(3))),
    )
    environment = {'x': Number(1)}

    machine = Machine(while_statement, environment)
    print machine.run()
