import io
import base64

from PIL import Image, ImageChops
from rdkit import Chem
from rdkit.Chem import Draw


def render_smiles(smiles):
    m = [Chem.MolFromSmiles(smiles)]
    img = Draw.MolsToGridImage(m)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode()
    im_url = "data:image/jpeg;base64, " + encoded_image

    return im_url
