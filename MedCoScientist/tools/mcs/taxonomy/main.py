from MedCoScientist.tools.mcs.pubmed import LitItem
import MedCoScientist.tools.mcs.taxonomy.type as taxonomy_type
import MedCoScientist.tools.mcs.taxonomy.litreview as litreview
import MedCoScientist.tools.mcs.taxonomy.observational.time as obs_time
import MedCoScientist.tools.mcs.taxonomy.observational.cohort as obs_cohort
import MedCoScientist.tools.mcs.taxonomy.experimental.distribution as exp_dist
import MedCoScientist.tools.mcs.taxonomy.experimental.enviornment as exp_env

def get_taxonomy(lit_item:LitItem, llm):
    args = {"title": lit_item.title, "abstract": lit_item.abstract}

    def _classify(module):
        chain = (module.prompt | llm.with_structured_output(module.StructuredResponse))
        result = chain.invoke(args)
        return result.category.value

    try:
        taxonomy = []
        study_type = _classify(taxonomy_type)
        taxonomy.append(('type', study_type))
        
        if study_type == 'observational':
            taxonomy.append(('time', _classify(obs_time)))
            taxonomy.append(('cohort', _classify(obs_cohort)))
        elif study_type == 'experimental':
            taxonomy.append(('distribution', _classify(exp_dist)))
            taxonomy.append(('enviornment', _classify(exp_envt)))
        elif study_type == 'litreview':
            taxonomy.append(('litreview', _classify(litreview)))
        return taxonomy
        
    except Exception as e:
        return []
    