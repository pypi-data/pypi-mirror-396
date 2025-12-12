# -*- coding: utf-8 -*-
import math

def apply_rounding(value, rounding=2):
    multiplier = 10 ** rounding
    return math.floor(round(value * multiplier + 0.5, rounding)) / multiplier


class Tribute:

    @staticmethod
    def get_tribute(tribute_type):
        """ Devuelve la instancia del tipo de percepcion deseado """
        if tribute_type == 'gross_income':
            return GrossIncome()
        elif tribute_type == 'profit':
            return Profit()
        elif tribute_type == 'suss':
            return Suss()
        else:
            raise NotImplementedError("El tipo de tributo {} No existe".format(tribute_type))

class Suss(object):

    def __init__(self):
        self.percentage = 0.0
        self.minimum_no_aplicable = 0.0
        self.minimum_tax = 0.0

    def calculate_value(self, amount_to_pay):
        """
        Devuelve el valor del calculo de IIBB
        :param amount_to_pay: Importe a pagar sin impuestos
        :return: Base imponible y Valor calculado
        """

        base = amount_to_pay
        value = apply_rounding(base * (self.percentage / 100))

        if base < self.minimum_no_aplicable or value < self.minimum_tax:
            value = 0

        return base, value

class GrossIncome(object):

    def __init__(self):
        self.percentage = 0.0
        self.minimum_no_aplicable = 0.0
        self.minimum_tax = 0.0

    def calculate_value(self, amount_to_pay):
        """
        Devuelve el valor del calculo de IIBB
        :param amount_to_pay: Importe a pagar sin impuestos
        :return: Base imponible y Valor calculado
        """

        base = amount_to_pay
        value = apply_rounding(base * (self.percentage / 100))

        if base < self.minimum_no_aplicable or value < self.minimum_tax:
            value = 0

        return base, value


class Activity:

    def __init__(self, minimum_no_aplicable, minimum_tax, percentage):
        """
        :param minimum_no_aplicable: Minimo no imponible de la actividad
        :param minimum_tax: Importe minimo a retener/percibir
        :param percentage: Porcentaje de la actividad
        """
        self.minimum_no_aplicable = minimum_no_aplicable
        self.minimum_tax = minimum_tax
        self.percentage = percentage


class Profit:

    def __init__(self):
        self.activity = None

    def calculate_value(self, accumulated, amount_to_pay, first_retention=True):
        """
        Devuelve el valor a retener/percibir para la actividad
        :param accumulated: Acumulado de pagos necesario para deducir el valor
        :param amount_to_pay: Importe a pagar sin impuestos
        :param first_retention: Si es la primera retencion, se restará el minimo no imponible
        :return: Base imponible y Valor que se debe retener
        """
        if not self.activity:
            raise AttributeError("Agregar actividad en el tributo antes de calcular el valor")

        minimum_no_aplicable = self.activity.minimum_no_aplicable
        # El acumulado se debe restar siempre, excepto en el caso que el acumulado sea mayor al minimo no imponible
        # y no se haya retenido por primera vez (porque no sobrepaso el minimo), entonces en ese caso el valor de la
        # retencion es por la anterior + la actual
        if ((accumulated - minimum_no_aplicable) * self.activity.percentage / 100) >= self.activity.minimum_tax\
                and first_retention:
            accumulated = minimum_no_aplicable

        base = amount_to_pay + accumulated - minimum_no_aplicable if first_retention else amount_to_pay + accumulated
        value = apply_rounding(base * (self.activity.percentage / 100))

        if value < self.activity.minimum_tax:
            value = 0

        return base, value
