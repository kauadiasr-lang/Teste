import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ser_consciente.aprendizado import gerar_nota_aprendizado
from ser_consciente.corpo import EstadoInterno
from ser_consciente.memoria import MemoriaAssociativa
from ser_consciente.persistencia import carregar, salvar
from ser_consciente.ser import Ser


class TestMemoriaAssociativa(unittest.TestCase):
    def test_reforca_conceitos_repetidos(self):
        m = MemoriaAssociativa()
        m.perceber("gato gosta de dormir")
        m.perceber("gato gosta de comer")
        self.assertGreaterEqual(m.conceitos["gato"].peso, 2.0)
        self.assertIn("gosta", m.conceitos["gato"].conexoes)

    def test_decaimento_reduz_peso_com_o_tempo(self):
        m = MemoriaAssociativa(taxa_decaimento=0.5)
        m.perceber("floresta")
        peso_inicial = m.conceitos["floresta"].peso
        m.decair()
        self.assertLess(m.conceitos["floresta"].peso, peso_inicial)

    def test_esquecimento_remove_conceitos_muito_fracos(self):
        m = MemoriaAssociativa(taxa_decaimento=0.9)
        m.perceber("eco")
        for _ in range(20):
            m.decair()
        self.assertNotIn("eco", m.conceitos)

    def test_perceber_registra_transicao_direcionada(self):
        m = MemoriaAssociativa()
        m.perceber("meu peixe nada")
        self.assertIsNotNone(m.transicao("meu", "peixe"))
        # direcionada -- a ordem inversa não foi observada, não deve existir
        self.assertIsNone(m.transicao("peixe", "meu"))

    def test_reforcar_transicao_positivo_e_negativo(self):
        m = MemoriaAssociativa()
        m.perceber("meu peixe nada")
        m.reforcar_transicao("meu", "peixe", 0.7)
        self.assertGreater(m.transicao("meu", "peixe").feedback, 0)
        m.reforcar_transicao("peixe", "meu", -1.3)
        self.assertLess(m.transicao("peixe", "meu").feedback, 0)

    def test_proxima_palavra_cadeia_evita_transicao_com_peso_negativo(self):
        m = MemoriaAssociativa()
        m.perceber("meu peixe nada")
        m.perceber("meu gato dorme")
        # derruba a transição meu->peixe bem fundo, e deixa meu->gato positiva
        m.reforcar_transicao("meu", "peixe", -10.0)
        m.reforcar_transicao("meu", "gato", 1.0)
        escolhas = {m.proxima_palavra_cadeia("meu") for _ in range(50)}
        self.assertNotIn("peixe", escolhas)


class TestAprendizado(unittest.TestCase):
    def test_nota_contraste_quando_ordens_opostas_tem_feedback_oposto(self):
        m = MemoriaAssociativa()
        m.perceber("meu peixe nada")
        m.reforcar_transicao("meu", "peixe", 1.0)
        m.reforcar_transicao("peixe", "meu", -1.0)
        nota = gerar_nota_aprendizado(
            m, [("peixe", "meu")], gostei=False, explicito=True, total_positivos=0
        )
        self.assertTrue("antes" in nota or "ordem" in nota)
        self.assertIn("meu", nota)
        self.assertIn("peixe", nota)


class TestEstadoInterno(unittest.TestCase):
    def test_descanso_recupera_energia_com_o_tempo_real(self):
        estado = EstadoInterno(energia=10.0)
        estado.ultima_atualizacao = time.time() - 100  # 100s de ausência simulada
        estado.tick()
        # recupera 100s * 0.2/s = 20, menos o custo metabólico fixo de 0.5
        self.assertAlmostEqual(estado.energia, 29.5, places=3)

    def test_tick_sem_ausencia_nao_recupera_energia(self):
        estado = EstadoInterno(energia=10.0)
        estado.tick()
        self.assertLess(estado.energia, 10.0)


class TestSer(unittest.TestCase):
    def test_responde_e_gera_pensamento(self):
        ser = Ser()
        resposta = ser.responder("o mar é imenso e azul")
        self.assertIsInstance(resposta, str)
        self.assertGreater(len(resposta), 0)
        self.assertEqual(ser.identidade.numero_interacoes, 1)

    def test_pensamentos_realimentam_a_memoria(self):
        ser = Ser()
        ser.responder("montanha e rio e vento")
        self.assertGreater(len(ser.memoria.conceitos), 0)
        self.assertGreater(len(ser.monologo), 0)

    def test_pensar_nao_introduz_vocabulario_novo_do_molde(self):
        ser = Ser()
        ser.perceber("floresta verde vento suave folhas caem devagar")
        conceitos_antes = set(ser.memoria.conceitos.keys())
        ser.pensar()
        conceitos_depois = set(ser.memoria.conceitos.keys())
        self.assertTrue(conceitos_depois.issubset(conceitos_antes))

    def test_estado_atual_nao_quebra_sem_memoria(self):
        ser = Ser()
        texto = ser.estado_atual()
        self.assertIn("Idade", texto)

    def test_dar_feedback_negativo_penaliza_transicao_usada(self):
        ser = Ser()
        ser.responder("meu peixe nada no aquário")
        ser.ultima_tentativa = ["meu", "peixe"]
        nota = ser.dar_feedback(gostei=False)
        self.assertLess(ser.memoria.transicao("meu", "peixe").feedback, 0)
        self.assertEqual(ser.total_feedback_negativo, 1)
        self.assertIn(nota, ser.diario_aprendizado)
        self.assertIsNone(ser.ultima_tentativa)

    def test_dar_feedback_positivo_explicito_reforca_transicao(self):
        ser = Ser()
        ser.responder("meu peixe nada no aquário")
        ser.ultima_tentativa = ["meu", "peixe"]
        ser.dar_feedback(gostei=True, explicito=True)
        self.assertGreater(ser.memoria.transicao("meu", "peixe").feedback, 0)
        self.assertEqual(ser.total_feedback_positivo, 1)

    def test_responder_resolve_tentativa_pendente_como_aceite_implicito(self):
        ser = Ser()
        ser.responder("meu peixe nada no aquário")
        ser.ultima_tentativa = ["meu", "peixe"]
        ser.responder("um dia comum")
        self.assertIsNone(ser.ultima_tentativa)
        self.assertEqual(ser.total_feedback_positivo, 1)

    def test_tentar_falar_sem_memoria_nao_gera_nada(self):
        ser = Ser()
        self.assertIsNone(ser.tentar_falar())


class TestPersistencia(unittest.TestCase):
    def test_mantem_memoria_e_identidade_entre_sessoes(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = os.path.join(tmp, "ser.json")
            ser = Ser()
            ser.responder("estrelas brilham na noite escura")
            nome_original = ser.identidade.nome
            salvar(ser, caminho)

            ser2 = carregar(caminho)
            self.assertEqual(ser2.identidade.nome, nome_original)
            self.assertEqual(ser2.identidade.numero_interacoes, 1)
            self.assertIn("estrelas", ser2.memoria.conceitos)

    def test_carregar_sem_arquivo_cria_ser_novo(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = os.path.join(tmp, "nao_existe.json")
            ser = carregar(caminho)
            self.assertEqual(ser.identidade.numero_interacoes, 0)

    def test_mantem_diario_e_transicoes_entre_sessoes(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = os.path.join(tmp, "ser.json")
            ser = Ser()
            ser.responder("meu peixe nada no aquário")
            ser.ultima_tentativa = ["meu", "peixe"]
            ser.dar_feedback(gostei=False)
            salvar(ser, caminho)

            ser2 = carregar(caminho)
            self.assertEqual(ser2.total_feedback_negativo, 1)
            self.assertEqual(ser2.diario_aprendizado, ser.diario_aprendizado)
            self.assertLess(ser2.memoria.transicao("meu", "peixe").feedback, 0)


if __name__ == "__main__":
    unittest.main()
