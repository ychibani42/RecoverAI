El ponente propone un flujo de trabajo de búsqueda de casos similares, basado en recuperación aumentada por generación (RAG), para la planificación de la recuperación ortopédica: indexar los historiales médicos del departamento —radiografías, diagnósticos y resultados clínicos— en una base de datos vectorial y ofrecer una interfaz mediante chatbot o agente para que los profesionales sanitarios puedan consultar “pacientes similares a este” utilizando factores estructurados como edad, tipo de fractura, nivel de actividad física o IMC.

El sistema devolvería los 5–10 casos más parecidos junto con sus protocolos de recuperación. La lógica es sencilla: el diagnóstico y las pruebas de imagen definen el caso, las características del paciente determinan la similitud y los resultados históricos sirven de base para proponer planes de recuperación.

El objetivo es mejorar la eficiencia y la consistencia clínica: los médicos obtienen orientación rápida y basada en evidencias para definir los tratamientos y los plazos de rehabilitación.

La vía de implementación técnica consiste en una arquitectura RAG —base de datos vectorial + índice + agente—, con canales de mensajería para pacientes como Telegram, Discord o WhatsApp como posibles extensiones opcionales.

No se trata de debatir sobre algoritmos, sino de convertir los datos históricos del departamento en una herramienta de apoyo a la toma de decisiones que reduzca la variabilidad entre los distintos planes asistenciales.

Arquitectura de apoyo a la decisión para la recuperación de casos similares

Mapeo problema-solución (Patrón D: Reto-Respuesta)

Situación actual: Los equipos de traumatología y ortopedia dependen del criterio individual y de registros dispersos para estimar los planes de recuperación de las fracturas, lo que genera variabilidad.

Carencia: No existe un mecanismo rápido para relacionar a un paciente actual con casos históricos prácticamente idénticos cuyos resultados ya se conocen.

Solución: Construir un sistema de búsqueda de casos basado en RAG que indexe radiografías, diagnósticos y atributos de los pacientes, y que devuelva los casos más similares junto con sus protocolos y plazos de recuperación.

Componentes del sistema (Patrón B: Ensamblaje estructural)

Datos de entrada: Imágenes radiográficas, notas diagnósticas y datos demográficos y atributos del paciente —edad, altura, peso, condición física/deportiva e indicadores de comorbilidad—.

Motor de similitud: Base de datos vectorial con embeddings indexados de los casos y filtros estructurados para factores clave, como rangos de edad o tipo de fractura.

Interfaz mediante agente: Chatbot que recibe consultas estructuradas como “hombre, 70 años, fractura de húmero, IMC X, deportista sí/no” y devuelve casos similares junto con los planes de recuperación recomendados.

Capa de comunicación (opcional):
