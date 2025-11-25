import logging
from langchain.tools.render import render_text_description
from langchain_core.tools import tool
from typing import Dict
from dotenv import load_dotenv
import os
from definitions import CONFIG_PATH
from pathlib import Path

from ChemCoScientist.frontend.memory import SELECTED_PAPERS
from ChemCoScientist.chemical_utils.ocr_pipeline import molecules_ocr, reactions_ocr

load_dotenv(CONFIG_PATH)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@tool
def detect_molecules(session_id: str = None) -> Dict:
    """
    Detects molecular structures in uploaded images and converts
    them into SMILES format using the `molecules_ocr` pipeline.

    The tool retrieves image paths either from:
    - `SELECTED_PAPERS[session_id]` if a session is active, or
    - an OCR input directory defined by the `OCR_IMAGES_PATH` environment
      variable.

    Parameters
    ----------
    session_id (str, optional): An identifier for the current user session.
            Used to access session-specific uploaded papers from `SELECTED_PAPERS`.

    Returns
    -------
    dict
        On success:  
        - A dictionary returned by `molecules_ocr`, mapping image filenames to lists
        of extracted SMILES strings.
        - An annotated image saved by `molecules_ocr` for each input image as <original_name>_annotated.jpg,
        containing bounding boxes around detected molecules.

        On failure or if no images are available:  
        A dictionary containing an `"answer"` key with an explanatory message.    
    """
    print('Running extract_molecules tool...')
    try:
        # TODO: remove when proper frontend is added
        if not SELECTED_PAPERS:
            directory = Path(os.environ.get('OCR_IMAGES_PATH'))
            images = [str(f.resolve()) for f in directory.iterdir() if f.is_file() and f.suffix.lower() == '.jpg']

            if not images:
                return {'answer': 'No images provided for OCR.'}
        else:
            if not SELECTED_PAPERS.get(session_id, []):
                return {'answer': 'No images provided for OCR.'}
            images = SELECTED_PAPERS[session_id]

        return molecules_ocr(images)
    except Exception as e:
        logger.error(f'molecules_ocr ERROR: {e}')
        return {'answer': 'Could not detect any molecules in the uploaded images.'}

@tool
def detect_reactions(session_id: str = None) -> Dict:
    """
    Detects chemical reactions in uploaded images and converts
    them into structured reaction elements format using the `reactions_ocr` pipeline.

    The tool retrieves image paths either from:
    - `SELECTED_PAPERS[session_id]` if a session is active, or
    - an OCR input directory defined by the `OCR_IMAGES_PATH` environment
      variable.

    Parameters
    ----------
    session_id (str, optional): An identifier for the current user session.
            Used to access session-specific uploaded papers from `SELECTED_PAPERS`.

    Returns
    -------
    dict
        On success:  
        - A dictionary returned by `reactions_ocr`, mapping image filenames to
        extracted reactants, conditions and products.
        - An annotated image saved by `reactions_ocr` for each input image as <original_name>_annotated.jpg
        containing bounding boxes around detected reaction elements.

        On failure or if no images are available:  
        A dictionary containing an `"answer"` key with an explanatory message.    
    """
    print('Running extract_reactions tool...')
    try:
        # TODO: remove when proper frontend is added
        if not SELECTED_PAPERS:
            directory = Path(os.environ.get('OCR_IMAGES_PATH'))
            images = [str(f.resolve()) for f in directory.iterdir() if f.is_file() and f.suffix.lower() == '.jpg']

            if not images:
                return {'answer': 'No images provided for OCR.'}
        else:
            if not SELECTED_PAPERS.get(session_id, []):
                return {'answer': 'No images provided for OCR.'}
            images = SELECTED_PAPERS[session_id]

        return reactions_ocr(images)
    except Exception as e:
        logger.error(f'reactions_ocr ERROR: {e}')
        return {'answer': 'Could not detect any reactions in the uploaded images.'}


chem_ocr_tools = [
    detect_molecules,
    detect_reactions
]

chem_ocr_tools_rendered = render_text_description(chem_ocr_tools)