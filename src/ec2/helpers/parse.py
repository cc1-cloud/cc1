# -*- coding: utf-8 -*-
# @COPYRIGHT_begin
#
# Copyright [2010-2014] Institute of Nuclear Physics PAN, Krakow, Poland
#
# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @COPYRIGHT_end
from ec2.error import InvalidFilter
import re

"""@package src.ec2.helpers.parse

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""

def parseSequenceArguments(parameters, prefix = '', suffix = ''):
    """
    Przeszukuje parametry w poszukiwaniu kluczy @prm{prefix}@val{numer}@prm{suffix}
    i zwraca wartości pod tymi kluczami
    """
    arguments = []
    counter = 1
    while True:
        argument = parameters.get( prefix + str( counter ) + suffix )

        if argument is None:
            break
        counter += 1

        arguments.append( argument )

    return arguments

    # inna wersja
    arguments = parameters

    if prefix:
        arguments = [argument for argument in arguments if argument.startwith( prefix )]
    if suffix:
        arguments = [argument for argument in arguments if argument.startwith( suffix )]

    # we now have list of matching arguments
    result_params = [ parameters[key] for key in arguments ]


def parseFilters(parameters):
    """
    Parsuje filtry. Szuka argumentów zaczynających się na 'Filter.' a kończących na '.Name',
    wartości tych argumentów będą kluczami słownika zwracanego. Następnie funkcja przeszukuje
    parametry w poszukiwaniu Filter.<numer filtra>.Value. Listę takową przypisuje do odpowiedniego
    miejsca w słowniku.

    @parameter{parameters,dict} Słownik parametrów przekazanych do serwera EC2 w requeście

    @response{dict(Filter.Name,[list]} Lista filtrów
    """

    filter_names = parseSequenceArguments(parameters, 'Filter.', '.Name')
    filters = {}
    filter_no = 1
    for filter in filter_names:
        filters[filter] = parseSequenceArguments(parameters, 'Filter.' + str(filter_no) + ".Value.")
        if not filters[filter]:
            raise InvalidFilter
        filter_no += 1

    return filters

def parseSequenceIntArguments(parameters, prefix = '', suffix = ''):
    """
    Wywołuje funkcję parseSequenceArguments z takimi samymi argumentami,
    a następnie rzutuje ja na integer. TODO ta funkcja chyba do wywalenia :D
    """
    temp_arguments = parseSequenceArguments(parameters, prefix, suffix)

    result_params = [ int(argument) for argument in temp_arguments ]

    return result_params

def parseID(entity, entity_type):
    """
    Sprawdza czy podany entity(String) - najczęściej odebrany jako request do serwera EC2
    jest poprawny. Jeżeli tak to zwraca ID bez przedrostka dla kompatybilności z CC1,
    w przeciwnym wypadku zwraca None.

    @parameter{entity,string} ID wybranego zasobu
    @parameter{entity_type,string} Wybrana wartość z Entities

    @response{
    """

    if entity.startswith( entity_type + '-' ):
        entity = entity.replace( entity_type + '-', '')
        return entity

    return None

def parseIDs(entities, entity_type):
    result = []
    for entity in entities:
        if entity.startswith( entity_type + '-' ):
            result.append( entity.replace( entity_type + '-', '') )
        else:
            return None
        print 'Entity:' ,entity
    print 'Entities:',result
    return result

def parseClmDate(clm_date):
    # CLM date format: 16.02.2014, 21:32:54
    # Amazon date format: YYYY-MM-DDTHH:MM:SS.000Z
    correctPattern = '^[0-9]{2}\.[0-9]{2}\.[0-9]{4}, [0-9]{2}:[0-9]{2}:[0-9]{2}$'
    pattern = re.compile( correctPattern )
    if not pattern.match(clm_date):
        return None

    day = str(clm_date[:2])
    month = str(clm_date[3:5])
    year = str(clm_date[6:10])
    time = str(clm_date[12:])

    ec2_date = year + '-' + month + '-' + day + 'T' + time
    return ec2_date
