import streamlit as st
from groq import Groq
from datetime import datetime
import json

st.set_page_config(page_title="Coach do Sono IA", page_icon="💤", layout="wide")

st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color:#EFF6FF; font-family:'Inter',sans-serif; }
    [data-testid="stSidebar"] { display:none; }
    .stTextInput>div>div>input, .stTextArea>div>textarea,
    .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color:#FFFFFF !important; color:#1A1A2E !important;
        border:1px solid #CED4DA !important; font-family:'Inter',sans-serif !important;
    }
    .stButton>button {
        width:100%; border-radius:10px; height:3.2em;
        background:linear-gradient(135deg,#1E3A8A,#1D4ED8) !important; color:white !important;
        font-weight:600; border:none; box-shadow:2px 2px 8px rgba(0,0,0,0.1);
        font-family:'Inter',sans-serif !important; transition:all 0.2s ease;
    }
    .stButton>button:hover { background:linear-gradient(135deg,#1D4ED8,#1E3A8A) !important; transform:translateY(-1px); }
    .stApp .stButton>button, .stApp .stButton>button p,
    .stApp .stButton>button span, .stApp .stButton>button div { color:white !important; }
    .stApp h1, .stApp h2, .stApp h3 { color:#1E3A8A !important; font-family:'Inter',sans-serif !important; font-weight:700 !important; }
    .card { background:linear-gradient(135deg,#EFF6FF,#DBEAFE); padding:20px; border-radius:14px; border:1px solid #93C5FD; margin-bottom:14px; white-space:normal; word-wrap:break-word; }
    .stApp .card, .stApp .card p, .stApp .card span, .stApp .card div, .stApp .card strong { color:#1E3A8A !important; }
    .card-blue { background:linear-gradient(135deg,#EFF6FF,#DBEAFE); padding:20px; border-radius:14px; border:1px solid #93C5FD; margin-bottom:14px; }
    .stApp .card-blue, .stApp .card-blue p, .stApp .card-blue div { color:#1E3A8A !important; }
    .card-red { background:linear-gradient(135deg,#FFF5F5,#FEE2E2); padding:20px; border-radius:14px; border:1px solid #FECACA; margin-bottom:14px; }
    .stApp .card-red, .stApp .card-red p, .stApp .card-red div { color:#7F1D1D !important; }
    .card-green { background:linear-gradient(135deg,#F0FDF4,#DCFCE7); padding:20px; border-radius:14px; border:1px solid #86EFAC; margin-bottom:14px; }
    .stApp .card-green, .stApp .card-green p, .stApp .card-green div { color:#14532D !important; }
    .card-yellow { background:linear-gradient(135deg,#FFFBEB,#FEF3C7); padding:18px; border-radius:12px; border:1px solid #FCD34D; margin-bottom:12px; }
    .stApp .card-yellow, .stApp .card-yellow p, .stApp .card-yellow div { color:#78350F !important; }
    .badge { background:#1E3A8A; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .badge-verde { background:#059669; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .badge-amarelo { background:#B45309; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .badge-roxo { background:#6D28D9; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .divider { border:none; height:1px; background:linear-gradient(to right,transparent,#93C5FD,transparent); margin:18px 0; }
    .hist-item { background:#FFFFFF; border-radius:10px; padding:12px 16px; margin-bottom:8px; border-left:4px solid #93C5FD; }
    .stApp .hist-item, .stApp .hist-item p, .stApp .hist-item span, .stApp .hist-item div { color:#1E3A8A !important; }
    .stat-box { background:#FFFFFF; border-radius:12px; padding:16px; text-align:center; border:1px solid #93C5FD; }
    .stApp .stat-box div, .stApp .stat-box span { color:#1E3A8A !important; }
    .chat-user { background:#FFFFFF; border:1px solid #93C5FD; border-radius:12px 12px 4px 12px; padding:12px 16px; margin:8px 0; }
    .stApp .chat-user, .stApp .chat-user p, .stApp .chat-user div { color:#1E3A8A !important; }
    .chat-persona { background:#DBEAFE; border:1px solid #93C5FD; border-radius:4px 12px 12px 12px; padding:12px 16px; margin:8px 0; }
    .stApp .chat-persona, .stApp .chat-persona p, .stApp .chat-persona div { color:#1E3A8A !important; }

    </style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = "Você é um especialista em medicina do sono e cronobiologia. Ajuda pessoas a melhorar a qualidade do sono com base em ciência do sono, higiene do sono e técnicas comprovadas. Nunca faz diagnósticos médicos. Português do Brasil."

@st.cache_resource
def get_cache_coach_sono():
    return {"perfis": {}}

_cache = get_cache_coach_sono()

CHAVES_SALVAR = ["usuario","historico_coach_sono"]

def gerar_json():
    return json.dumps({k: st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith("_") and k not in ("api_key",)}, ensure_ascii=False, indent=2, default=str)

def carregar_json_sessao(dados):
    _bloq = {'api_key','etapa','nome_login','chave_login','upload_login','btn_entrar_login'}
    _pref = (
        'btn_','sel_','ul_','dl_','cad_','_sub','_sm','_tab','_bsc',
        'ativo_','rem_','sel_pet_','ev_','prof_','hig_','prev_',
        'vac_','sint_','comp_','trad_','subs_','amb_','viag_','chat_',
        'duvida_','emerg_','peso_','data_','obs_','tipo_','vet_','desc_',
        'local_','prox_','alim','sit_emerg_','tc_','oraf','siau','agmag',
        'lv','mv','pt','pi','sh','wc','rv','rp','rc',
    )
    import re as _re
    for k, v in dados.items():
        if k in _bloq: continue
        if any(k.startswith(p) for p in _pref): continue
        if _re.match(r'.+_\d+$', k): continue
        st.session_state[k] = v

def salvar_perfil_cache(usuario):
    _cache["perfis"][usuario] = {k: st.session_state.get(k) for k in CHAVES_SALVAR}

def perfis_salvos():
    return [p for p in _cache["perfis"].keys() if len(p.strip()) >= 2]

def carregar_perfil_cache(usuario):
    return _cache["perfis"].get(usuario)

defaults = {
    "etapa": "Login", "usuario": "", "api_key": "",
    "historico_coach_sono": [],
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── LOGIN ──
if st.session_state.etapa == "Login":
    st.markdown("# 💤 Coach do Sono IA")
    st.markdown("<div class=\'card\'><b>🔒 ACESSO RESTRITO A CLIENTES DO QUIZ COM PRÊMIOS</b><br>🔗 <a href='https://quizcompremios.com.br' target='_blank' style='color:#4F46E5;font-weight:700;text-decoration:underline;'>quizcompremios.com.br</a></div>", unsafe_allow_html=True)
    st.info("💻 **Dica:** Pela complexidade dos agentes, no computador a experiência é mais agradável.")
    with st.container():
        nome  = st.text_input("Seu Nome:", key="nome_login")
        chave = st.text_input("🔑 Sua Chave API da Groq:", type="password", key="chave_login")
        arq_j = st.file_uploader("📂 Carregar dados salvos (.json):", type=["json"], key="upload_login")
        dados_login = json.load(arq_j) if arq_j else None
        if st.button("✨ ENTRAR", key="btn_entrar_login"):
            if len(nome.strip()) < 2:
                st.warning("Digite um nome com pelo menos 2 caracteres.")
            elif chave.strip():
                st.session_state.usuario = nome.strip()
                st.session_state.api_key = chave
                if dados_login: carregar_json_sessao(dados_login)
                st.session_state.etapa = "App"
                st.rerun()
            else:
                st.warning("Preencha nome e chave API.")

elif st.session_state.etapa == "App":
    historico = st.session_state.get("historico_coach_sono", [])
    salvar_perfil_cache(st.session_state.usuario)

    _tab_home_sono, _tab_perfil_sono, _tab_rotina_noturna, _tab_rotina_manha, _tab_habitos_sono, _tab_sabotadores, _tab_plano21, _tab_higiene, _tab_relaxamento, _tab_diario_sono, _tab_evolucao_sono = st.tabs(['🏠 Home', '📋 Meu Perfil do Sono', '🌙 Rotina Noturna', '☀️ Rotina Matinal', '📊 Análise de Hábitos', '⚠️ Sabotadores', '🗓️ Plano 21 Dias', '😴 Higiene do Sono', '🧘 Técnicas de Relaxamento', '📓 Diário do Sono', '📈 Evolução'])

    # ── BARRA SALVAR — aparece em todas as abas ──
    with st.expander("💾 Salvar / Carregar meus dados", expanded=False):
        _bsc1, _bsc2 = st.columns(2)
        with _bsc1:
            import json as _jsv
            _dsv = {k: st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith('_') and k not in ('api_key',)}
            st.download_button("💾 Baixar meus dados (.json)",
                data=_jsv.dumps(_dsv, ensure_ascii=False, indent=2, default=str),
                file_name=f"dados_{st.session_state.get('usuario','user')}.json",
                mime="application/json", key="dl_barra_sv_coachson")
        with _bsc2:
            _fupsv = st.file_uploader("📂 Carregar dados salvos:", type=["json"], key="ul_barra_sv_coachson", label_visibility="collapsed")
            if _fupsv:
                try:
                    import json as _jld
                    for _k2,_v2 in _jld.loads(_fupsv.read().decode()).items():
                        if _k2 not in ('api_key','etapa'): st.session_state[_k2] = _v2
                    st.success("✅ Dados restaurados!"); st.rerun()
                except: st.error("Arquivo inválido.")


    with _tab_home_sono:
        st.title(f"💤 Olá, {st.session_state.usuario}!")
        st.markdown(f"*Durma melhor, viva mais — seu coach de sono com IA.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown(f"### Bem-vindo ao **Coach do Sono IA**")
        st.markdown(f"<div class='card'>Use as abas acima para navegar entre as funcionalidades. Cada aba oferece uma ferramenta diferente com IA.</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>🏠</div><div style='font-size:0.8em;'>Coach do Sono IA</div></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>🤖</div><div style='font-size:0.8em;'>Powered by IA</div></div>", unsafe_allow_html=True)
        with col3: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>💾</div><div style='font-size:0.8em;'>Salve seus dados</div></div>", unsafe_allow_html=True)
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        col_sv, _ = st.columns([1,3])
        with col_sv:
            st.download_button("💾 Salvar dados (.json)", data=json.dumps({k: st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith("_") and k not in ("api_key",)}, ensure_ascii=False, indent=2, default=str), file_name=f"coach_sono_{st.session_state.usuario}.json", mime="application/json", key="dl_coach__1")

    with _tab_perfil_sono:
        st.header("📋 Meu Perfil do Sono")
        prompt_perfil_sono = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_perfil_sono", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_perfil_sono", use_container_width=True):
            if prompt_perfil_sono.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_perfil_sono}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_perfil_sono = resp.choices[0].message.content
                        if resultado_perfil_sono: st.session_state['res_perfil_sono_coachs1'] = str(resultado_perfil_sono)
                        st.session_state["res_perfil_sono"] = resultado_perfil_sono
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Meu Perfil do Sono","resumo":prompt_perfil_sono[:60],"conteudo":resultado_perfil_sono})
                        st.session_state.historico_coach_sono = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_perfil_sono"):
            st.markdown(f"<div class='card'>{st.session_state['res_perfil_sono']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_perfil_sono"], file_name="perfil_sono_resultado.txt", mime="text/plain", key="dl_perfil_sono")

    with _tab_rotina_noturna:
        st.header("🌙 Rotina Noturna")
        prompt_rotina_noturna = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_rotina_noturna", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_rotina_noturna", use_container_width=True):
            if prompt_rotina_noturna.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_rotina_noturna}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_rotina_noturna = resp.choices[0].message.content
                        if resultado_rotina_noturna: st.session_state['res_rotina_notur_coachs2'] = str(resultado_rotina_noturna)
                        st.session_state["res_rotina_noturna"] = resultado_rotina_noturna
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Rotina Noturna","resumo":prompt_rotina_noturna[:60],"conteudo":resultado_rotina_noturna})
                        st.session_state.historico_coach_sono = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_rotina_noturna"):
            st.markdown(f"<div class='card'>{st.session_state['res_rotina_noturna']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_rotina_noturna"], file_name="rotina_noturna_resultado.txt", mime="text/plain", key="dl_rotina_noturna")

    with _tab_rotina_manha:
        st.header("☀️ Rotina Matinal")
        prompt_rotina_manha = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_rotina_manha", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_rotina_manha", use_container_width=True):
            if prompt_rotina_manha.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_rotina_manha}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_rotina_manha = resp.choices[0].message.content
                        if resultado_rotina_manha: st.session_state['res_rotina_manha_coachs3'] = str(resultado_rotina_manha)
                        st.session_state["res_rotina_manha"] = resultado_rotina_manha
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Rotina Matinal","resumo":prompt_rotina_manha[:60],"conteudo":resultado_rotina_manha})
                        st.session_state.historico_coach_sono = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_rotina_manha"):
            st.markdown(f"<div class='card'>{st.session_state['res_rotina_manha']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_rotina_manha"], file_name="rotina_manha_resultado.txt", mime="text/plain", key="dl_rotina_manha")

    with _tab_habitos_sono:
        st.header("📊 Análise de Hábitos")
        prompt_habitos_sono = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_habitos_sono", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_habitos_sono", use_container_width=True):
            if prompt_habitos_sono.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_habitos_sono}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_habitos_sono = resp.choices[0].message.content
                        if resultado_habitos_sono: st.session_state['res_habitos_sono_coachs4'] = str(resultado_habitos_sono)
                        st.session_state["res_habitos_sono"] = resultado_habitos_sono
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Análise de Hábitos","resumo":prompt_habitos_sono[:60],"conteudo":resultado_habitos_sono})
                        st.session_state.historico_coach_sono = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_habitos_sono"):
            st.markdown(f"<div class='card'>{st.session_state['res_habitos_sono']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_habitos_sono"], file_name="habitos_sono_resultado.txt", mime="text/plain", key="dl_habitos_sono")

    with _tab_sabotadores:
        st.header("⚠️ Sabotadores")
        prompt_sabotadores = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_sabotadores", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_sabotadores", use_container_width=True):
            if prompt_sabotadores.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_sabotadores}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_sabotadores = resp.choices[0].message.content
                        if resultado_sabotadores: st.session_state['res_sabotadores_coachs5'] = str(resultado_sabotadores)
                        st.session_state["res_sabotadores"] = resultado_sabotadores
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Sabotadores","resumo":prompt_sabotadores[:60],"conteudo":resultado_sabotadores})
                        st.session_state.historico_coach_sono = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_sabotadores"):
            st.markdown(f"<div class='card'>{st.session_state['res_sabotadores']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_sabotadores"], file_name="sabotadores_resultado.txt", mime="text/plain", key="dl_sabotadores")

    with _tab_plano21:
        st.header("🗓️ Plano 21 Dias")
        prompt_plano21 = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_plano21", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_plano21", use_container_width=True):
            if prompt_plano21.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_plano21}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_plano21 = resp.choices[0].message.content
                        if resultado_plano21: st.session_state['res_plano21_coachs6'] = str(resultado_plano21)
                        st.session_state["res_plano21"] = resultado_plano21
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Plano 21 Dias","resumo":prompt_plano21[:60],"conteudo":resultado_plano21})
                        st.session_state.historico_coach_sono = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_plano21"):
            st.markdown(f"<div class='card'>{st.session_state['res_plano21']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_plano21"], file_name="plano21_resultado.txt", mime="text/plain", key="dl_plano21")

    with _tab_higiene:
        st.header("😴 Higiene do Sono")
        prompt_higiene = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_higiene", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_higiene", use_container_width=True):
            if prompt_higiene.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_higiene}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_higiene = resp.choices[0].message.content
                        if resultado_higiene: st.session_state['res_higiene_coachs7'] = str(resultado_higiene)
                        st.session_state["res_higiene"] = resultado_higiene
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Higiene do Sono","resumo":prompt_higiene[:60],"conteudo":resultado_higiene})
                        st.session_state.historico_coach_sono = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_higiene"):
            st.markdown(f"<div class='card'>{st.session_state['res_higiene']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_higiene"], file_name="higiene_resultado.txt", mime="text/plain", key="dl_higiene")

    with _tab_relaxamento:
        st.header("🧘 Técnicas de Relaxamento")
        prompt_relaxamento = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_relaxamento", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_relaxamento", use_container_width=True):
            if prompt_relaxamento.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_relaxamento}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_relaxamento = resp.choices[0].message.content
                        if resultado_relaxamento: st.session_state['res_relaxamento_coachs8'] = str(resultado_relaxamento)
                        st.session_state["res_relaxamento"] = resultado_relaxamento
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Técnicas de Relaxamento","resumo":prompt_relaxamento[:60],"conteudo":resultado_relaxamento})
                        st.session_state.historico_coach_sono = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_relaxamento"):
            st.markdown(f"<div class='card'>{st.session_state['res_relaxamento']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_relaxamento"], file_name="relaxamento_resultado.txt", mime="text/plain", key="dl_relaxamento")

    with _tab_diario_sono:
        st.header("📓 Diário do Sono")
        prompt_diario_sono = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_diario_sono", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_diario_sono", use_container_width=True):
            if prompt_diario_sono.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_diario_sono}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_diario_sono = resp.choices[0].message.content
                        if resultado_diario_sono: st.session_state['res_diario_sono_coachs9'] = str(resultado_diario_sono)
                        st.session_state["res_diario_sono"] = resultado_diario_sono
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Diário do Sono","resumo":prompt_diario_sono[:60],"conteudo":resultado_diario_sono})
                        st.session_state.historico_coach_sono = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_diario_sono"):
            st.markdown(f"<div class='card'>{st.session_state['res_diario_sono']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_diario_sono"], file_name="diario_sono_resultado.txt", mime="text/plain", key="dl_diario_sono")

    with _tab_evolucao_sono:
        st.header("📈 Evolução")
        prompt_evolucao_sono = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_evolucao_sono", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_evolucao_sono", use_container_width=True):
            if prompt_evolucao_sono.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_evolucao_sono}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_evolucao_sono = resp.choices[0].message.content
                        if resultado_evolucao_sono: st.session_state['res_evolucao_son_coachs10'] = str(resultado_evolucao_sono)
                        st.session_state["res_evolucao_sono"] = resultado_evolucao_sono
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Evolução","resumo":prompt_evolucao_sono[:60],"conteudo":resultado_evolucao_sono})
                        st.session_state.historico_coach_sono = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_evolucao_sono"):
            st.markdown(f"<div class='card'>{st.session_state['res_evolucao_sono']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_evolucao_sono"], file_name="evolucao_sono_resultado.txt", mime="text/plain", key="dl_evolucao_sono")


# --- RODAPÉ ---
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;font-size:0.75em;color:#94A3B8;'>© 2026 Coach do Sono IA · Quiz Com Prêmios</div>", unsafe_allow_html=True)
