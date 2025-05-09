USE [Sage]
GO

/****** Object:  View [dbo].[VIS_FUR_StockWebService]    Script Date: 09/05/2025 19:00:01 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


ALTER VIEW [dbo].[VIS_FUR_StockWebService] AS
SELECT 
	CASE WHEN Vis_MB_EstocsWEB.codigocolor_ IS NOT NULL AND Vis_MB_EstocsWEB.codigocolor_ <> ''  THEN
  CONCAT(UPPER(LTRIM(RTRIM(Vis_MB_EstocsWEB.CodigoArticulo))),'-',Vis_MB_EstocsWEB.codigocolor_) 
  ELSE UPPER(LTRIM(RTRIM(Vis_MB_EstocsWEB.CodigoArticulo)))
  END AS idconecta,
  Floor(Vis_MB_EstocsWEB.unidades) AS quantity,
  Vis_MB_EstocsWEB.FechaRecepcion AS available_date,
  CASE WHEN Articulos.ObsoletoLc = -1 THEN 0
  ELSE 2
  END AS out_of_stock,
  CASE WHEN Vis_FechaUltimoMovPendiente.FechaRegistro IS NULL THEN CASE
      WHEN VIS_FechaUltimoMovLot.FechaRegistro IS NULL THEN CASE
        WHEN Vis_FechaUltimoMov.FechaRegistro IS NULL THEN
        Vis_FechaUltimoMovLot_NoP.FechaRegistro
        ELSE Vis_FechaUltimoMov.FechaRegistro END
      ELSE VIS_FechaUltimoMovLot.FechaRegistro END
    ELSE Vis_FechaUltimoMovPendiente.FechaRegistro END AS LastModified
FROM Vis_MB_EstocsWEB
  LEFT JOIN CodigosTallaColor ON CodigosTallaColor.CodigoEmpresa =
    Vis_MB_EstocsWEB.CodigoEmpresa AND CodigosTallaColor.CodigoArticulo =
    Vis_MB_EstocsWEB.CodigoArticulo AND CodigosTallaColor.CodigoColor_ =
    Vis_MB_EstocsWEB.codigocolor_
  LEFT JOIN Articulos
    ON Articulos.CodigoEmpresa = Vis_MB_EstocsWEB.CodigoEmpresa AND
    Articulos.CodigoArticulo = Vis_MB_EstocsWEB.CodigoArticulo
  LEFT OUTER JOIN Vis_FechaUltimoMov ON Vis_FechaUltimoMov.CodigoEmpresa =
    Vis_MB_EstocsWEB.CodigoEmpresa AND Vis_FechaUltimoMov.CodigoColor_ =
    Vis_MB_EstocsWEB.codigocolor_ AND Vis_FechaUltimoMov.CodigoArticulo =
    Vis_MB_EstocsWEB.CodigoArticulo
  LEFT OUTER JOIN Vis_FechaUltimoMovLot_NoP
    ON Vis_FechaUltimoMovLot_NoP.codigoempresa = Vis_MB_EstocsWEB.CodigoEmpresa
    AND Vis_FechaUltimoMovLot_NoP.CodigoColor_ = Vis_MB_EstocsWEB.codigocolor_
    AND Vis_FechaUltimoMovLot_NoP.codigoarticulo =
    Vis_MB_EstocsWEB.CodigoArticulo
  LEFT OUTER JOIN VIS_FechaUltimoMovLot ON VIS_FechaUltimoMovLot.codigoempresa =
    Vis_MB_EstocsWEB.CodigoEmpresa AND VIS_FechaUltimoMovLot.CodigoColor_ =
    Vis_MB_EstocsWEB.codigocolor_ AND VIS_FechaUltimoMovLot.codigoarticulo =
    Vis_MB_EstocsWEB.CodigoArticulo
  LEFT OUTER JOIN Vis_FechaUltimoMovPendiente
    ON Vis_FechaUltimoMovPendiente.CodigoEmpresa =
    Vis_MB_EstocsWEB.CodigoEmpresa AND Vis_FechaUltimoMovPendiente.CodigoColor_
    = Vis_MB_EstocsWEB.codigocolor_ AND
    Vis_FechaUltimoMovPendiente.CodigoArticulo = Vis_MB_EstocsWEB.CodigoArticulo
WHERE Vis_MB_EstocsWEB.CodigoArticulo NOT IN ('SILLA165', 'MESA006', 'MESA039',
  'LAMP031')
GO


