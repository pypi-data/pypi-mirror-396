import pandas as pd
from .urothelial import DataProcessorUrothelial
from .merge_utils import merge_dataframes
from IPython import embed     

if __name__ == "__main__":
    processor = DataProcessorUrothelial()

    enhanced_file_path = "example/data/Enhanced_AdvUrothelial.csv"
    demographics_file_path = "example/data/Demographics.csv"
    #practice_file_path = "flatiron_cleaner/data/Practice.csv"
    #mortality_file_path = "flatiron_cleaner/data/Enhanced_Mortality_V2.csv"
    #biomarkers_file_path = "data/Enhanced_MetPC_Biomarkers.csv"
    ecog_file_path = "example/data/ECOG.csv"
    vitals_file_path = "example/data/Vitals.csv"
    #lab_file_path =  "data/Lab.csv"
    medication_file_path =  "example/data/MedicationAdministration.csv"
    #diagnosis_file_path = "data/Diagnosis.csv"
    insurance_file_path = "example/data/Insurance.csv"

    df = pd.read_csv(enhanced_file_path)
    
    # Process datasets
    #enhanced_df = processor.process_enhanced(enhanced_file_path, 
    #                                         primary_treatment_path = "data_mpc/Enhanced_MetPC_PrimaryTreatment.csv",
    #                                         drop_dates = False)

    demographics_df = processor.process_demographics(demographics_file_path, 
                                                     index_date_df=df, 
                                                     index_date_column='AdvancedDiagnosisDate')
    
    #practice_df = processor.process_practice(practice_file_path)

    #mortality_df = processor.process_mortality(file_path="data_crc/Enhanced_Mortality_V2.csv",
    #                                            index_date_df=df,
    #                                            index_date_column='MetDiagnosisDate',
    #                                            supplementary_files = {'data_crc/Visit.csv' : ['VisitDate'], 'data_crc/Telemedicine.csv' : ['VisitDate'], 'data_crc/Enhanced_MetCRC_Orals.csv' : ['StartDate', 'EndDate']})
    
    #biomarkers_df = processor.process_biomarkers(biomarkers_file_path,
    #                                             index_date_df=df,
    #                                             index_date_column='MetDiagnosisDate',
    #                                             days_before=None,
    #                                             days_after=14)

    ecog_df =  processor.process_ecog(ecog_file_path,
                                      index_date_df=df,
                                      index_date_column='AdvancedDiagnosisDate',
                                      days_before=90,
                                      days_after=0,
                                      days_before_further=360)
    
    vitals_df = processor.process_vitals(vitals_file_path,
                                         index_date_df=df,
                                         index_date_column='AdvancedDiagnosisDate',
                                         weight_days_before = 90,
                                         days_after = 0,
                                         vital_summary_lookback = 180,
                                         abnormal_reading_threshold = 1)
    
    #labs_df = processor.process_labs(lab_file_path,
    #                                 index_date_df=df,
    #                                 index_date_column='MetDiagnosisDate',
    #                                 days_before = 90,
    #                                 days_after = 0,
    #                                 summary_lookback = 180)
    
    medications_df = processor.process_medications(medication_file_path,
                                                   index_date_df = df,
                                                   index_date_column='AdvancedDiagnosisDate',
                                                   days_before=180,
                                                   days_after=0)
    

    #diagnosis_df = processor.process_diagnosis(diagnosis_file_path,
    #                                           index_date_df = df,
    #                                           index_date_column='MetDiagnosisDate',
    #                                           days_before=None,
    #                                           days_after=0)
      
    insurance_df = processor.process_insurance(insurance_file_path,
                                               index_date_df = df,
                                               index_date_column='AdvancedDiagnosisDate',
                                               days_before=None,
                                               days_after=14,
                                               missing_date_strategy = 'conservative')
    


    # Merge datasets
    merged_data = merge_dataframes(ecog_df,
                                   vitals_df,
                                   medications_df,
                                   insurance_df,
                                   demographics_df)
    if merged_data is not None:
        print(merged_data.head())
        print(merged_data.dtypes)
        embed()