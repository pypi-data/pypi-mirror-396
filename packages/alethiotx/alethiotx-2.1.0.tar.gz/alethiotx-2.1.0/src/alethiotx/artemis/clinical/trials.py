from requests import get
from datetime import date
from typing import List
from typing import List
from pandas import DataFrame, concat, isna, json_normalize

def _indication_regexp(indication: str = 'Breast Cancer') -> str:
    """
    Generate a regular expression pattern for filtering medical indications.

    This function returns a regex pattern that matches various forms and abbreviations
    of a specified medical indication. If the indication is not found in the lookup
    table, it returns a wildcard pattern and prints a warning message.

    :param indication: The medical indication to generate a regex pattern for.
                       Must match one of the predefined indications in the lookup table.
                       Defaults to ``Breast Cancer``.
    :type indication: str, optional

    :return: A regular expression pattern string that matches the specified indication
             and its common variations. Returns ``.*`` (wildcard) if indication not found.
    :rtype: str

    :raises: None - prints a warning message if indication is not recognized

    **Supported Indications**
    * ``Myeloproliferative Neoplasm``
    * ``Breast Cancer``
    * ``Lung Cancer``
    * ``Prostate Cancer``
    * ``Bowel Cancer``
    * ``Melanoma``
    * ``Diabetes Mellitus Type 2``
    * ``Cardiovascular Disease``

    **Example**
    >>> _indication_regexp('Breast Cancer')
    '.*[Bb]reast.+[Cc]ancer.*|.*[Bb]reast.+[Cc]arcinoma.*|.*[Cc]arcinoma.+[Bb]reast.*'
    
    >>> _indication_regexp('Unknown Condition')
    Selected indication: Unknown Condition is not known. Proceeding with the full list of indications.
    '.*'

    .. warning::

       The function performs case-sensitive matching on the indication parameter
       against the lookup table. Ensure the indication string exactly matches one
       of the supported values.
    """
    pattern = '.*'

    lookup = DataFrame({
        'indication': [
            'Myeloproliferative Neoplasm',  
            'Breast Cancer', 
            'Lung Cancer',
            'Prostate Cancer',
            'Bowel Cancer',
            'Melanoma',
            'Diabetes Mellitus Type 2',
            'Cardiovascular Disease'
        ],
        'regexp': [
            r'.*MPN.*|.*MDS.*|.*[Mm]yeloproliferative.*|.*[Mm]yelofibrosis.*|.*[Pp]olycythemia.*|.*[Tt]hrombocytha?emia.*|.*[Mm]yelodysplastic.*|.*[Nn]eoplasm.*',
            r'.*[Bb]reast.+[Cc]ancer.*|.*[Bb]reast.+[Cc]arcinoma.*|.*[Cc]arcinoma.+[Bb]reast.*',
            r'.*[Cc]arcinoma.+[Bb]ronch.*|.*MDS.*|.*[Ll]ung.+[Cc]ancer.*|.*[Ll]ung.+[Cc]arcinoma.*|.*[Ll]ung.+[Tt]umor.*',
            r'.*[Cc]arcinoma.+[Pp]rostate.*|.*[Pp]rostat.+[Cc]ancer.*|.*[Pp]rostat.+[Cc]arcinoma.*',
            r'.*[Cc]olon.+[Cc]ancer.*|.*[Rr]ectal.+[Cc]ancer.*|.*[Rr]ectal.+[Cc]arcinoma.*',
            r'.*[Mm]elanoma.*|.*[Ss]kin.+[Ll]esion.*',
            r'.*[Tt]ype.+2.*|.*[Tt]ype.+ii.*|.*[Tt]ype-2.*|.*[Tt]ype-ii.*|.*[Tt]2[Dd][Mm].*',
            r'.*cvd.*|.*[Aa]rteriosclero.*|.*[Aa]thero.*|.*[Cc]ardiovascular [Dd]isease.*|.*[Mm]yocardial.*|[Aa]cute [Cc]oronary [Ss]yndrome.+|[Cc]ardi.+|[Cc]oronary.+|[Hh]eart [Dd]isease.+|[Pp]eripheral [Aa]rtery [Dd]isease.+|.*[Vv]ascular [Dd]isease.+'
        ]
    })

    if indication in lookup['indication'].tolist():
        pattern = list(lookup.loc[lookup['indication'] == indication, 'regexp'])[0]
    else: print('Selected indication: ' + indication + ' is not known. Proceeding with the full list of indications.')

    return pattern

def fetch(search: str = 'Breast Cancer', filter_by_regexp: bool = True, fields: List[str] = ['NCTId', 'OverallStatus', 'StudyType', 'Condition', 'InterventionType', 'InterventionName', 'Phase', 'StartDate'], interventional_only: bool = True, intervention_types: List[str] = ['DRUG', 'BIOLOGICAL'], last_6_years: bool = True) -> DataFrame:
    """
    Retrieve and filter clinical trials data from ClinicalTrials.gov API.
    This function queries the ClinicalTrials.gov API for clinical trials matching
    the specified search criteria and applies various filters to refine the results.
    :param search: The condition or disease to search for in clinical trials.
        Default is ``Breast Cancer``.
    :type search: str
    :param filter_by_regexp: Whether to filter results by disease-related indications
        using regular expression matching. Default is True.
    :type filter_by_regexp: bool
    :param fields: List of field names to retrieve from the API. Default includes
        ``NCTId``, ``OverallStatus``, ``StudyType``, ``Condition``, ``InterventionType``,
        ``InterventionName``, ``Phase``, and ``StartDate``.
    :type fields: List[str]
    :param interventional_only: Whether to filter results to include only
        interventional studies. Default is True.
    :type interventional_only: bool
    :param intervention_types: List of intervention types to include in results.
        Default is [``DRUG``, ``BIOLOGICAL``].
    :type intervention_types: List[str]
    :param last_6_years: Whether to filter results to include only trials that
        started within the last 6 years. Default is True.
    :type last_6_years: bool
    :return: A DataFrame containing filtered clinical trials data with columns for
        ``NCTId``, ``OverallStatus``, ``StudyType``, ``InterventionType``, ``InterventionName``, ``Phase``,
        and ``StartDate``. Returns None if no results are found.
    :rtype: DataFrame or None
    :raises: None - The function handles empty results by printing a message and
        returning None.

    **Example**
    >>> df = get_clinical_trials(search='Breast Cancer', last_6_years=False)
    >>> print(df.head())
    """
    search_url = search.replace(" ", "+")
    fields = '%2C'.join(fields)

    print(f"Fetching clinical trials for search term: {search}...")
    resp = get('https://www.clinicaltrials.gov/api/v2/studies?query.cond=' + search_url + '&pageSize=1000' + '&markupFormat=legacy' + '&fields=' + fields)
    txt = resp.json()

    # if there are no results
    if txt['studies'] == []:
        print('Your request did not return any data. Please check request spelling/words and try again.')
        return

    res = json_normalize(txt['studies'])

    while 'nextPageToken' in txt:
        resp = get('https://www.clinicaltrials.gov/api/v2/studies?query.cond=' + search_url + '&pageSize=1000'  + '&markupFormat=legacy' + '&pageToken=' + txt['nextPageToken'] + '&fields=' + fields)
        txt = resp.json()
        res = concat([res, json_normalize(txt['studies'])])

    print(f"Fetched {res.shape[0]} clinical trials before filtering.")

    res.rename(columns={
        'protocolSection.identificationModule.nctId': 'NCTId', 
        'protocolSection.statusModule.overallStatus': 'OverallStatus',
        'protocolSection.statusModule.startDateStruct.date': 'StartDate',
        'protocolSection.conditionsModule.conditions': 'Condition',
        'protocolSection.designModule.studyType': 'StudyType',
        'protocolSection.designModule.phases': 'Phase', 
        'protocolSection.armsInterventionsModule.interventions': 'Interventions'
    }, inplace=True)

    # remove trials with no intervention name and no phase
    res = res[~res["Interventions"].isna()]
    res = res[~res["Phase"].isna()]

    # filter empty phases and select maximum phase (last value in the list, if there are multiple phases)
    res = res[res["Phase"].str.len() != 0]
    res['Phase'] = res['Phase'].apply(lambda x: x if len(x) == 1 else x.pop())

    # unlist phase column
    res = res.explode('Phase')
    res = res[res['Phase'] != 'NA']

    # filter and rename phases
    res.loc[res['Phase'] == 'PHASE0', 'Phase'] = 'PHASE1'
    res.loc[res['Phase'] == 'EARLY_PHASE1', 'Phase'] = 'PHASE1'
    res.loc[res['Phase'] == 'PHASE4', 'Phase'] = 'PHASE3'
    res.loc[res['Phase'] == 'PHASE5', 'Phase'] = 'PHASE3'

    # unlist interventions
    res = res.explode('Interventions')
    res['InterventionType'] = res['Interventions'].apply(lambda x: x['type'])
    res['InterventionName'] = res['Interventions'].apply(lambda x: x['name'])
    res = res.drop(['Interventions'], axis=1)

    # unlist items in columns
    res = res.explode('NCTId')
    res = res.explode('OverallStatus')
    res = res.explode('StudyType')
    res = res.explode('Condition')
    res = res.explode('StartDate')

    # select only interventional trials
    if interventional_only:
        res = res[res['StudyType'] == 'INTERVENTIONAL']
        res = res[(res['InterventionType'].isin(intervention_types))]

    # filter by disease related indications
    if filter_by_regexp:
        regexp_pattern = _indication_regexp(search)
        res = res[res['Condition'].str.match(regexp_pattern)]

    res = res.drop(['Condition'], axis=1)
    res = res.drop_duplicates()
    
    # convert date to year
    res['StartDate'] = res['StartDate'].apply(lambda x: int(str(x)[0:4]) if not isna(x) else x)

    if last_6_years:
        current_year = int(date.today().strftime("%Y"))
        res = res[res['StartDate'] >= current_year - 6]

    # remove duplicates
    res = res.drop_duplicates().reset_index(drop=True)

    print(f"{res.shape[0]} clinical trials remain after filtering.")

    return(res)

# run when file is directly executed
if __name__ == '__main__': 
    trs = fetch(search="Breast Cancer")
    print(trs)
    trs.to_csv("breast_clinical_trials.csv", index = False)
