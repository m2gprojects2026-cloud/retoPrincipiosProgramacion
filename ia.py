from transformers import pipeline

clasificador = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

def recomendar(historial):

    categorias = [
        "Cambio de aceite",
        "Revisión de frenos",
        "Cambio de filtros",
        "Alineación y balanceo",
        "Revisión general"
    ]

    resultado = clasificador(
        historial,
        categorias
    )

    return resultado["labels"][0]
