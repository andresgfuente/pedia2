import streamlit as st
import random
#As Langchain team has been working aggresively on improving the tool, we can see a lot of changes happening every weeek,
#As a part of it, the below import has been depreciated
#from langchain.llms import OpenAI
import datetime
import time
import boto3
import json
import botocore.config
from abc import ABC, abstractmethod
from typing import List
#When deployed on huggingface spaces, this values has to be passed using Variables & Secrets setting, as shown in the video :)
#import os
#os.environ["OPENAI_API_KEY"] = "sk-werwerwerrtertertwkFJwtwetwteWSig4ZY9AT"

#Function to return the response

class RagAnswer:
    def __init__(self, response: str, context_list: List[str]):
        self.response = response
        self.context_list = context_list

class RagAgent(ABC):
    def __init__(
        self,
        knowledge_base_id: str,
        top_k: int,
        temperature: float,
        max_token_count: int
    ):
        self.knowledge_base_id = knowledge_base_id
        self.top_k = top_k
        self.temperature = temperature
        self.max_token_count = max_token_count

        self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime',region_name='us-east-1')
        self.bedrock_runtime = boto3.client('bedrock-runtime',region_name='us-east-1')
        
    def retrieve_context(self, query: str) -> List[str]:
        retrieval_results = self.bedrock_agent_runtime.retrieve(
            retrievalQuery={"text": query},
            knowledgeBaseId=self.knowledge_base_id,
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": self.top_k}
            }
        )["retrievalResults"]

        return [x["content"]["text"] for x in retrieval_results]

    def augment_query(self, query: str, context_list: List[str]) -> str:
        prompt = "\n\nEres un asistente virtual que responde preguntas\n"
        prompt += f"Query: {query}\n"
        prompt += f"Context:\n\n"
        for context in context_list:
            prompt += f"{context}\n\n"
        prompt += "Responde la pregunta basado en el contexto que te proporcione"
        return prompt

    @abstractmethod
    def get_response_from_model(self, model_prompt: str) -> str:
        pass
        
    def answer_question(self, question: str)-> RagAnswer:
        context_list = self.retrieve_context(question)
        model_prompt = self.augment_query(question, context_list)
        model_response = self.get_response_from_model(model_prompt)
        return RagAnswer(model_response, context_list)


class TitanRagAgent(RagAgent):
    def __init__(
        self,
        knowledge_base_id: str,
        top_k: int = 5,
        temperature: float = 0.1,
        max_token_count: int = 4000
    ):
        super().__init__(knowledge_base_id, top_k, temperature, max_token_count)
        self.model_id ="amazon.titan-text-express-v1"

    def get_response_from_model(self, model_prompt: str) -> str:
        

        body = {
            "inputText": model_prompt,
            "textGenerationConfig":
           {
               "temperature": self.temperature,
            
                "maxTokenCount": self.max_token_count,
            }
        }

        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id, body=json.dumps(body)
        )

        response_body = json.loads(response["body"].read())

        return response_body["results"][0]["outputText"]


client_s3 = boto3.client('s3')












frases_simpaticas = [
    "La vida es como una caja de chocolates, pero sin las calorías.",
    "Si te caes siete veces, levántate ocho. O mejor aún, consigue un cojín más cómodo.",
    "La sonrisa es el idioma universal, pero no olvides que el café también ayuda.",
    "La paciencia es una virtud, pero también lo es saber cuándo pedir pizza.",
    "No te preocupes por el mañana, a menos que seas un aspirador robótico.",
    "No importa cuán lento vayas, siempre estás adelantando a los que están en el sofá.",
    "La vida es como un videojuego, pero sin los botones de reinicio.",
    "No todo el que divaga está perdido, a menos que haya olvidado su GPS.",
    "Si la vida te da limones, haz limonada. Si te da sandía, invita a tus amigos a una fiesta.",
    "La felicidad está en las pequeñas cosas, como encontrar dinero en un abrigo viejo o que el semáforo cambie a verde justo cuando llegas.",
    "No soy perezoso, solo estoy en modo de ahorro de energía.",
    "No se puede comprar la felicidad, pero sí puedes comprar helado, que es casi lo mismo.",
    "La mente es como un paracaídas, funciona mejor cuando está abierta, pero también es útil tener un buen seguro.",
    "El dinero no puede comprar el amor, pero sí puede comprar una pizza, que es bastante parecido.",
    "La mejor manera de olvidar tus problemas es recordar que hay alguien por ahí con problemas peores. Y si no los hay, siempre puedes mirar Twitter."
]

TA=TitanRagAgent(knowledge_base_id='YADE4FYYLV')

usuarios_permitidos = ['andresg','valeriar','sergioab']

def validar_usuario(username):
    if username in usuarios_permitidos:
        return True
    else:
        return False

def get_text():
    input_text = st.text_input("En que puedo ayudarte? ", key="input")
    return input_text 
   
def click_button(boton):
    st.session_state[boton] = not st.session_state[boton]



if 'clicked' not in st.session_state:
    st.session_state.clicked = False
if 'username' not in st.session_state:
    st.session_state['username'] ='' 
if 'respuesta' not in st.session_state:
    st.session_state['respuesta']=None
if 'resultado' not in st.session_state:
    st.session_state['resultado']=None
if 'boton1' not in st.session_state:
    st.session_state['boton1']=False
if 'boton2' not in st.session_state:
    st.session_state['boton2']=False
if 'boton3' not in st.session_state:
    st.session_state['boton3']=False
if 'descripcion1' not in st.session_state:
    st.session_state['descripcion1']=None
    
def change_name(bool,descripcion,bool1,name):
    st.session_state[descripcion] = name
    st.session_state[bool] = bool1
    
st.set_page_config(page_title="Itaupedia", page_icon=':robot:')

st.header('Bienvenidos a Itaupedia!')

#st.markdown("<h2 style='color:black;'>Bienvenidos a Itaupedia!</h2>", unsafe_allow_html=True)
#st.markdown("<h6 style='color:black;'>Itaupedia es un chatbot interno diseñado para facilitar el acceso y la búsqueda de información dentro de la organización. Alimentado por una amplia base de datos de documentos internos, Itaupedia puede responder preguntas sobre políticas, procedimientos, y cualquier otro tipo de información relevante para los empleados.</h6>", unsafe_allow_html=True)


st.sidebar.title('Ingrese su nombre de Usuario')
st.session_state['username']=st.sidebar.text_input('Username:',  type='default')
validado=False
if st.sidebar.button("Validar Usuario"):
        if validar_usuario(st.session_state['username'].lower()):
            st.sidebar.success('Usuario Validado Correctamente')
            validado=True
            #st.write(f"Bienvenido, {st.session_state['username']}!")        
        else:
            st.sidebar.error('Error en el ingreso del Nombre de Usuario')               
if validado:
    st.write('Bienvenido',st.session_state['username'])
user_input=get_text()

respondido=False
submit = st.button('Enviar pregunta')
if submit and validar_usuario(st.session_state['username']):
    frase_aleatoria = random.choice(frases_simpaticas)
    with st.spinner("📢"+frase_aleatoria):
        resp=TA.answer_question(user_input)
        response=resp.response
        st.subheader("Respuesta:")
        st.write(response)
        #time.sleep(5)
        st.subheader("Encuesta de satisfacción")
        st.write("Por favor, indique su grado de acuerdo con la siguiente afirmación:")
        respondido=True

        col1, col2, col3 = st.columns(3)

        # Botones con caritas
        with col1:
            if st.checkbox('😊 Feliz', key='feliz',on_change=click_button,args=['boton1']):
                st.success('Seleccionaste la carita feliz')

        with col2:
            if st.checkbox('😐 Neutro', key='neutro',on_change=click_button,args=['boton2']):
                st.info('Seleccionaste la carita neutra')

        with col3:
            if st.checkbox('😠 Enojado', key='enojado',on_change=click_button,args=['boton3']):
                st.error('Seleccionaste la carita enojada')

    # The message and nested widget will remain on the page
        
        today=datetime.datetime.today()
        year=today.year
        month=today.month
        day=today.day

        filename='itaupedia'+today.strftime('%Y_%M_%d-%H_%M_%S')
        particion=f'/year={str(year)}/month={str(month)}/day={str(day)}/'
        data_dict={'Usuario':st.session_state['username'],'Pregunta':user_input,'Respuesta':response,'Puntaje':st.session_state.descripcion1,'boton1':st.session_state.boton1,'boton2':st.session_state.boton2,'boton3':st.session_state.boton3}
        data_string=json.dumps(data_dict,indent=2,default=str)
        response_s3=client_s3.put_object(Bucket='preguntasrespondidas',Body=data_string,Key=f'preguntasrespondidas/{particion}{filename}.json')

        
        
        
elif  not submit:
    pass
elif validar_usuario(st.session_state['username'])==False: # If username isn't defined yet
    st.warning("Por favor valide que se haya ingresado correctamente su usuario o que no este vacio el campo de Username.")
elif validar_usuario==False:
    st.write('Error en el ingreso del Nombre de Usuario')
else:
    st.write('Error en el ingreso del Nombre de Usuario')


        


#if resultado is not None:
 #   st.write("¡Gracias por tu feedback!")

    # Llamar a las funciones de los botones y colocarlos en las columnas respectivas

