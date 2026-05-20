from pydantic import BaseModel


class HeaderRenderedDTO(BaseModel):
    '''Simple class that just indicates that the header has been rendered. 
    It can be used as a signal for other components to know when to render themselves.'''
    
    #pode ter outros atributos depois, mas por enquanto só precisamos de um sinal booleano
    rendered: bool