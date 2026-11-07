# TanIA: revisión de literatura

IA, offloading cognitivo y aprendizaje de programación · noviembre de 2026

## Resumen

La evidencia respalda la premisa de TanIA: en programación, la IA sube el rendimiento en la tarea pero no el aprendizaje, y lo que decide el daño es **cómo** se le pregunta, no **cuánto** se la usa.

- Varios ensayos aleatorizados llegan al mismo resultado: con IA se termina mejor la tarea, pero el conocimiento y la comprensión de código no suben, o bajan (Anthropic: 50 % frente a 67 % en el quiz; TUM, N = 275: sin ganancia de conocimiento).
- Dentro del grupo con IA hay una brecha enorme según el patrón de uso: entre 24 % y 39 % de acierto para quienes delegan, frente a entre 65 % y 86 % para quienes preguntan para entender.
- Las queries se pueden clasificar: hay tipologías publicadas y LLMs que clasifican pedidos de ayuda con un acuerdo cercano al de dos humanos.
- Las intervenciones que funcionan son metacognitivas: pistas de planificación, preguntas guía y explicar antes de pegar. Eso es justo lo que hace una query reformulada.
- Lo que no encontramos: ninguna herramienta que diagnostique el **historial** de una persona a lo largo del tiempo y entre herramientas. Tampoco hay estudios en el Perú o en América Latina.

## Rendimiento no es aprendizaje

Cinco experimentos muestran que la IA mejora el producto, pero deja igual o peor la comprensión de quien lo hizo.

| Estudio | Diseño | Hallazgo |
| --- | --- | --- |
| [Shen y Tamkin, Anthropic (2026)](https://www.anthropic.com/research/AI-assistance-coding-skills) | Ensayo aleatorizado, N = 52, librería nueva de Python | Con IA: 50 % en el quiz frente a 67 % sin IA. La mayor brecha está en depuración. Sin ganancia significativa de velocidad. |
| [Bassner et al. (2025), TUM](https://consensus.app/papers/details/4ba657dd763c5dd0b39ce09ededdebba/) | Ensayo aleatorizado, N = 275, curso introductorio | ChatGPT y un tutor con andamiaje suben la nota del ejercicio. Ninguno mejora la ganancia de conocimiento ni la comprensión de código. |
| [Sankaranarayanan (2026)](https://consensus.app/papers/details/cf176f7b162851d890159c644d769a47/) | Experimento, N = 78, plugin de Cursor | IA libre: 77 % de fracaso al mantener el código sin IA. Con una "puerta de explicación": 39 %. |
| [Fan et al. (2024)](https://consensus.app/papers/details/a2a806ce679a5073a16075b2507626ae/) | Ensayo aleatorizado, N = 117, escritura | El grupo con ChatGPT mejoró más su ensayo, sin más ganancia ni transferencia de conocimiento. Lo llaman "pereza metacognitiva". |
| [Prather et al. (2024)](https://consensus.app/papers/details/650a177891a1556faf385ee57bf006ec/) | 21 sesiones con eye tracking | Quienes ya sabían aceleran. Quienes tenían dificultades terminan con una "ilusión de competencia". |

Para TanIA, la implicancia es que **no basta con medir cuánto se usa la IA**. El daño aparece en la comprensión, la depuración y el mantenimiento, que son invisibles en el producto final.

## No toda delegación es igual

La distinción central es la de Kirschner, retomada por [Sankaranarayanan (2026)](https://consensus.app/papers/details/cf176f7b162851d890159c644d769a47/): **descargar** carga cognitiva irrelevante está bien, pero **tercerizar** la carga que forma esquemas mentales impide aprender. Quienes aprenden bien con IA la tratan como un consultor, no como un contratista.

Lo que muestran los logs de queries:

- **Seis modos de interacción** ([Anthropic, 2026](https://www.anthropic.com/research/AI-assistance-coding-skills)). Tres modos tienen bajo aprendizaje: delegar, la dependencia progresiva y la depuración iterativa con IA (24 % a 39 % en el quiz). Otros tres tienen alto aprendizaje: generar y pedir explicación, preguntar conceptos y programar solo usando la IA para verificar (65 % a 86 %).
- **Copiar y pegar el enunciado.** En [Amoozadeh et al. (2024)](https://consensus.app/papers/details/e7b25fb23829583f8e6f717bfaac3a1d/), cerca de un tercio de los intentos fue pegar la tarea completa sin esfuerzo propio, y pocos verificaron. En [Sawalha et al. (2024)](https://consensus.app/papers/details/1070782ed36a541db8ccc25bdec9a663/), el 26 % siempre copió y pegó. Quienes hacían varias preguntas sucesivas rindieron mejor en el examen final.
- **El círculo vicioso.** En [Rahe et al. (2025)](https://consensus.app/papers/details/bab41c82b96b5aaa8c77064372ab56c4/), los estudiantes entraban en un ciclo: pegaban el código generado, fallaba y pedían el arreglo. Quienes usaban IA con regularidad pedían más soluciones completas.
- **Ayuda inmediata y poco contexto.** En 2,500 queries de un curso de data science ([Sheese et al., 2023](https://consensus.app/papers/details/800c3bd08370555a9b77ad822afb541f/)), la mayoría pedía ayuda inmediata con la tarea, pocas buscaban entender conceptos, y los estudiantes daban muy poca información.
- **Qué se asocia a mejores notas.** En [StudyChat (2025)](https://consensus.app/papers/details/2df19ae512c55ea7b631ebb02138e567/), con 16,851 interacciones, pedir comprensión conceptual se asocia a mejores notas, y usar el LLM para esquivar los objetivos de la tarea, a peores exámenes.
- **Mecánica del proceso.** [Liu et al. (2026)](https://consensus.app/papers/details/6b833d2249b35454ad2d8d16d5b1ad28/) proponen una teoría fundamentada con dos bucles, andamiaje y offloading. Documentan una "calibración metacognitiva atenuada": los estudiantes se sienten más preparados de lo que están. Es el insumo del diagnóstico de TanIA.

## Qué funciona: andamiaje metacognitivo

Las intervenciones que protegen el aprendizaje empujan al usuario a planificar, monitorear y evaluar antes de recibir código. Eso es lo que hace una buena reformulación de query.

- **Pistas de planificación.** En un curso introductorio de data science con 102 estudiantes, pedir pistas de planificación se asoció con mejores notas en todos los niveles. Ante tareas difíciles, los estudiantes pedían más ayuda para depurar, no para planificar ([Phung et al., 2025](https://consensus.app/papers/details/1747b86072fd5e9ea1fe14bc015d529a/)).
- **Recordatorios de proceso en vivo.** En un ensayo aleatorizado con 122 estudiantes de un curso de Python, un agente que vigilaba los logs y lanzaba recordatorios no directivos llevó a planificar más, depurar con más precisión y sacar mejores notas ([Hou et al., 2026](https://consensus.app/papers/details/990fea8043885c73a6f035de4ccc87f3/)).
- **Preguntas guía para formular el prompt.** Los estudiantes con preguntas guía programaban y verificaban por su cuenta. Sin ellas, pegaban el código en ChatGPT ([Sun et al., 2024](https://consensus.app/papers/details/3922d9a124dd59d897e567b6d0a63432/)).
- **Explicar antes de integrar.** La "puerta de explicación", que exige explicar el código antes de pegarlo, bajó el fracaso sin IA de 77 % a 39 % ([Sankaranarayanan, 2026](https://consensus.app/papers/details/cf176f7b162851d890159c644d769a47/)).

Con eso, cada reformulación sugerida puede justificarse con un mecanismo concreto: planificar, explicar o verificar.

## Viabilidad técnica

Clasificar queries con un LLM ya se hizo con buena precisión, y hay datos públicos de queries reales de estudiantes.

- **Clasificador.** GPT-4 clasificó pedidos de ayuda de un curso introductorio sin ejemplos previos, y un modelo afinado alcanzó un acuerdo comparable al de dos evaluadores humanos ([Savelka et al., 2023](https://consensus.app/papers/details/de17d1853ab95204abaf068c5077eb7d/)). Con un modelo abierto local (Gemma) se logró 82 % de acuerdo con humanos, kappa = 0.74 ([Abrar et al., 2026](https://consensus.app/papers/details/ed6a466080675ceeb23508461db31c10/)).
- **Datos públicos para el demo.** [StudyChat](https://consensus.app/papers/details/2df19ae512c55ea7b631ebb02138e567/) (UMass) tiene 16,851 interacciones de 203 estudiantes con ChatGPT, ya etiquetadas.

## Tipología v0

Tomamos los seis modos de Anthropic como base, porque están medidos con resultados de aprendizaje, y les sumamos lo que dicen los estudios de logs. Cada query recibe un modo, la habilidad que deja de ejercitar y una reformulación sugerida.

| Modo | Aprendizaje | Query típica | Habilidad que no se ejercita | Reformulación sugerida | Respaldo en logs |
| --- | --- | --- | --- | --- | --- |
| Delegación total | Bajo | "Hazme una función que limpie esta base" (con el enunciado pegado) | Descomponer el problema y diseñar | "Quiero limpiar esta base. ¿En qué pasos lo dividirías? Dame solo el primero y yo intento el código." | Cerca de un tercio pegó la tarea completa (Amoozadeh); 26 % siempre copió y pegó (Sawalha) |
| Depuración iterativa | Bajo | "No funciona, arréglalo" + traceback | Leer errores y depurar | "¿Qué significa este error y en qué línea buscarías? No me des el arreglo todavía." | Ciclo de pegar código, que falle y pedir el arreglo (Rahe) |
| Dependencia progresiva | Bajo | Empieza preguntando y termina en "escríbelo tú" | Persistir ante la dificultad | "Revísame este intento y dime dónde está el primer problema." | Bucle de offloading sostenido con sobreconfianza (Liu) |
| Generar y explicar | Alto | "Escríbelo y explícame cada línea" | (se preserva) | Mantener, y pedir un ejercicio parecido para hacerlo solo | Explicar antes de integrar baja el fracaso de 77 % a 39 % (Sankaranarayanan) |
| Pregunta conceptual | Alto | "¿Cuándo conviene usar apply en vez de un bucle?" | (se preserva) | Mantener | Asociada a mejores notas (StudyChat), pero es la menos frecuente (Sheese) |
| Verificar lo propio | Alto | "Escribí esto, ¿mi razonamiento es correcto?" | (se preserva) | Mantener | El feedback de verificación tiene la mayor continuación productiva, 82.4 % (Abrar) |

Además de los seis modos, cada query se marca en dos ejes que vienen de la literatura de logs:

- **Contexto aportado:** enunciado pegado tal cual, reformulado o pregunta propia.
- **Esfuerzo previo visible:** si la query muestra un intento propio o no.

El diagnóstico agrega todo esto en el tiempo: qué habilidades se ejercitan poco y si la persona está pasando de modos bajos a modos altos.

## Brechas y cautelas

**Lo que nadie hace todavía:**

- **Un diagnóstico longitudinal del propio historial.** Los estudios analizan sesiones de laboratorio o un semestre, y los productos existentes solo cuentan mensajes. Los modos de aprendizaje de Claude Code y el Study Mode de ChatGPT cambian la respuesta de la IA, pero no le muestran a la persona su patrón.
- **El contexto latinoamericano y las ciencias sociales.** No encontramos estudios en el Perú ni en América Latina. Casi todos son de cursos de ciencias de la computación en EE. UU., Europa o China.

**Cautelas:**

- Varios estudios son correlacionales (Gerlich, StudyChat). Los ensayos aleatorizados son de corto plazo, de 35 a 90 minutos.
- El estudio de Anthropic lo hizo una empresa de IA. Lo citamos junto con TUM y Sankaranarayanan, que llegan a lo mismo.
- En TUM, el tutor que no daba soluciones tampoco mejoró el conocimiento, aunque sí la motivación. TanIA no promete que aprenderás más: promete que verás qué estás dejando de practicar.

## Referencias

- Abrar et al. (2026). [When LLM Tutoring Responses Work](https://consensus.app/papers/details/ed6a466080675ceeb23508461db31c10/). ArXiv.
- Amoozadeh et al. (2024). [Student-AI Interaction: A Case Study of CS1 students](https://consensus.app/papers/details/e7b25fb23829583f8e6f717bfaac3a1d/). Koli Calling.
- Bassner et al. (2025). [Less stress, better scores, same learning](https://consensus.app/papers/details/4ba657dd763c5dd0b39ce09ededdebba/). Computers and Education: AI.
- Fan et al. (2024). [Beware of Metacognitive Laziness](https://consensus.app/papers/details/a2a806ce679a5073a16075b2507626ae/). BJET.
- Gerlich (2025). [AI tools in society: cognitive offloading and critical thinking](https://doi.org/10.3390/soc15010006). Societies.
- Hou et al. (2026). [Bridging awareness and behavior](https://consensus.app/papers/details/990fea8043885c73a6f035de4ccc87f3/). Frontiers in Psychology.
- Lee et al. (2025). [The Impact of Generative AI on Critical Thinking](https://advait.org/files/lee_2025_ai_critical_thinking_survey.pdf). CHI.
- Liu et al. (2026). [Tool, tutor, or crutch?](https://consensus.app/papers/details/6b833d2249b35454ad2d8d16d5b1ad28/). International Journal of STEM Education.
- McNichols et al. (2025). [The StudyChat Dataset](https://consensus.app/papers/details/2df19ae512c55ea7b631ebb02138e567/). LAK26.
- Phung et al. (2025). [Plan More, Debug Less](https://consensus.app/papers/details/1747b86072fd5e9ea1fe14bc015d529a/). ArXiv.
- Prather et al. (2024). [The Widening Gap](https://consensus.app/papers/details/650a177891a1556faf385ee57bf006ec/). ICER.
- Rahe et al. (2025). [How Do Programming Students Use Generative AI?](https://consensus.app/papers/details/bab41c82b96b5aaa8c77064372ab56c4/). ACM on Software Engineering.
- Sankaranarayanan (2026). [Mitigating "Epistemic Debt"](https://consensus.app/papers/details/cf176f7b162851d890159c644d769a47/). ArXiv.
- Savelka et al. (2023). [Efficient Classification of Student Help Requests](https://consensus.app/papers/details/de17d1853ab95204abaf068c5077eb7d/). ArXiv.
- Sawalha et al. (2024). [Analyzing student prompts and their effect on ChatGPT's performance](https://consensus.app/papers/details/1070782ed36a541db8ccc25bdec9a663/). Cogent Education.
- Sheese et al. (2023). [Patterns of Student Help-Seeking](https://consensus.app/papers/details/800c3bd08370555a9b77ad822afb541f/). ACE.
- Shen y Tamkin (2026). [How AI assistance impacts the formation of coding skills](https://www.anthropic.com/research/AI-assistance-coding-skills). Anthropic.
- Sun et al. (2024). [Prompt-based learning in ChatGPT](https://consensus.app/papers/details/3922d9a124dd59d897e567b6d0a63432/). HSS Communications.
