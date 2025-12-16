from enum import Enum


class EFaseRetificacao(Enum):
    NaoIniciado = 0
    SolicitacaoXml = 1
    AguardandoXml = 2
    DownloadXml = 3
    ExtraindoDadosDoXml = 4
    AguardandoRubrica = 5
    #? Abertura de Competencia
    EstruturandoXmlAberturaCompetencia = 6
    AberturaDeCompetencia = 7
    ConsultandoESocialAberturaCompetencia = 8
    #? Rubricas 
    EstruturandoXmlInclusaoRubricas = 9
    InclusaoDasRubricas = 10
    ConsultandoESocialInclusaoRubricas = 11
    #? Exclusao de Pagamentos
    EstruturandoXmlExclusaoPagamentos = 12
    ExclusaoDePagamentos = 13
    ConsultandoESocialExclusaoPagamentos = 14
    #? Retificacao
    EstruturandoXmlRetificacaoRemuneracao = 15
    RetificacaoDaRemuneracao = 16
    ConsultandoESocialRetificacaoRemuneracao = 17
    #? Desligamento
    EstruturandoXmlDesligamento = 18
    Desligamento = 19
    ConsultandoESocialDesligamento = 20
    #? Inclusao de Pagamentos
    EstruturandoXmlInclusaoPagamentos = 21
    InclusaoDosPagamentos = 22
    ConsultandoESocialInclusaoPagamentos = 23
    #? Fechamento de Competencia
    EstruturandoXmlFechamentoCompetencia = 24
    FechamentoDeCompetencia = 25
    ConsultandoESocialFechamentoCompetencia = 26
    Finalizado = 27
