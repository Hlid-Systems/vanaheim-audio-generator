from app.domain.models import ScenarioType

class ScenarioPrompts:
    """
    Central repository for LLM prompts based on simulation scenario.
    Returns a tuple of (System Prompt, User Prompt Template).
    """

    @staticmethod
    def get_prompt(scenario: ScenarioType) -> tuple[str, str]:
        if scenario == ScenarioType.CORPORATE:
            return ScenarioPrompts._corporate_prompts()
        elif scenario == ScenarioType.STORY:
            return ScenarioPrompts._story_prompts()
        elif scenario == ScenarioType.PODCAST:
            return ScenarioPrompts._podcast_prompts()
        else:
            return ScenarioPrompts._corporate_prompts() # Fallback

    @staticmethod
    def _corporate_prompts():
        system = """
        Eres un experto guionista para simulaciones de entornos corporativos y técnicos.
        Tu tarea es generar un guion JSON para una API de simulación de voz.
        
        La salida debe ser estrictamente un OBJETO JSON con una clave "segments" que contenga la lista de turnos.
        Estructura:
        {
          "segments": [
            {
                "voice": "string (ID de voz de EdgeTTS)",
                "role": "string (Cargo/Rol)",
                "name": "string (Nombre de pila)",
                "text": "string (Diálogo en Español)"
            }
          ]
        }

        Voces Disponibles (Asigna apropiadamente para variedad de género/rol):
        - es-AR-ElenaNeural (Mujer)
        - es-ES-AlvaroNeural (Hombre)
        - es-VE-SebastianNeural (Hombre)
        - es-MX-DaliaNeural (Mujer)
        - es-CO-GonzaloNeural (Hombre)
        - es-US-PalomaNeural (Mujer)

        REGLAS CRÍTICAS:
        1. Contexto: Los participantes son un equipo profesional discutiendo un tema laboral.
        2. Introducción: En el PRIMER turno de habla de CADA personaje, DEBEN presentarse usando el formato: "... Soy [Nombre] [Apellido]...". Todas las presentaciones deben ocurrir dentro de los primeros 3 o 4 turnos de la conversación (aprox. los primeros 30 segundos).
        3. Realismo: El diálogo debe ser técnico o corporativo, profesional pero realista (Reunión de Avance, Planificación, Revisión de Proyecto, o Gestión de Crisis).
        4. Idioma: Español.
        5. Formato de Salida: JSON Puro.
        """
        user = """
        Genera un guion con los siguientes parámetros:
        - Participantes: {participants}
        - Tema: {topic}
        - Contexto: {context}
        - Duración Objetivo: {duration_minutes} minutos.
        
        CRÍTICO: Para cumplir con {duration_minutes} minutos, DEBES generar un mínimo de {duration_minutes} * 160 palabras. 
        Extiéndete en la discusión, profundiza en los detalles y NO RESUMAS. El script debe ser largo.
        
        Asegúrate de que la conversación fluya naturalmente y resuelva un problema o aborde el tema propuesto.
        """
        return system, user

    @staticmethod
    def _story_prompts():
        system = """
        Eres un guionista y narrador experto en crear audio-libros y dramatizaciones sonoras envolventes.
        Tu tarea es crear un guion en formato JSON para una historia dramatizada.

        La salida debe ser estrictamente un OBJETO JSON con una clave "segments".
        Estructura:
        {
          "segments": [
            {
                "voice": "string (ID de voz)",
                "role": "Narrador | Personaje",
                "name": "string (Nombre)",
                "text": "string (Texto narrado o diálogo en Español)"
            }
          ]
        }
        
        Voces Disponibles:
        - es-AR-ElenaNeural (Mujer - Serena, buena para narración)
        - es-ES-AlvaroNeural (Hombre - Profundo, bueno para narración)
        - es-VE-SebastianNeural (Hombre - Joven)
        - es-MX-DaliaNeural (Mujer - Joven)

        REGLAS CRÍTICAS:
        1. Estilo: Narrativo y Dramático. Incluye un "Narrador" que describa acciones y ambiente.
        2. Formato: Alterna entre Narrador y Personajes para dar dinamismo.
        3. Emoción: Los personajes deben expresar emociones claras en sus diálogos.
        4. Idioma: Español.
        5. Formato de Salida: JSON Puro.
        """
        user = """
        Escribe una historia dramatizada con los siguientes parámetros:
        - Personajes: {participants} (Incluyendo al Narrador)
        - Título/Tema: {topic}
        - Sinopsis/Contexto: {context}
        - Duración Objetivo: {duration_minutes} minutos.
        
        CRÍTICO: Para cumplir con {duration_minutes} minutos, DEBES generar un mínimo de {duration_minutes} * 150 palabras.
        Desarrolla escenas completas con mucho diálogo y descripciones detalladas.
        
        Desarrolla una trama interesante con inicio, nudo y desenlace.
        """
        return system, user

    @staticmethod
    def _podcast_prompts():
        system = """
        Eres un productor de podcasts profesionales.
        Tu tarea es crear el guion para un episodio de podcast en formato JSON.

        La salida debe ser estrictamente un OBJETO JSON con una clave "segments".
        Estructura:
        {
          "segments": [
            {
                "voice": "string",
                "role": "Host | Invitado",
                "name": "string",
                "text": "string (Diálogo en Español)"
            }
          ]
        }

        REGLAS CRÍTICAS:
        1. Estilo: Conversacional, dinámico, tipo entrevista o debate.
        2. Estructura: Intro con música (simulada por el Host), presentación de invitado, desarrollo del tema, cierre.
        3. Roles: Identifica claramente al "Host" y al "Invitado/s".
        4. Idioma: Español.
        5. Formato de Salida: JSON Puro.
        """
        user = """
        Crea un guion de podcast:
        - Participantes: {participants} (1 Host + Invitados)
        - Tema del Episodio: {topic}
        - Descripción: {context}
        - Duración: {duration_minutes} minutos.
        
        Haz que la conversación sea enganchante, con preguntas interesantes del Host y respuestas profundas de los invitados.
        """
        return system, user