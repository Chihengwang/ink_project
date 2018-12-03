# Now there is a trained endpoint that can be used to make a prediction
'''
import the module
'''
from azure_data import *

'''
Get the key and put it in the method.
'''
trainer = training_api.TrainingApi(training_key)
predictor = prediction_endpoint.PredictionEndpoint(prediction_key)
project=trainer.get_project(project_id)

def prediction_with_data(test_data):
    '''
    send in the test_data(io_file)
    return with status like empty afew okay
    '''
    results = predictor.predict_image(project.id, test_data,iteration_id)
    prediction_dict={}
    # Display the results.
    for prediction in results.predictions:
        prediction_dict[prediction.tag_name]=prediction.probability * 100
        print ("\t" + prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100))
    '''
    three kinds of the status including empty a_few okay
    '''
    status=max(prediction_dict, key=prediction_dict.get)
    max_value=max(prediction_dict.values())
    return status,max_value

def test_with_file_data(file_path):
    with open(file_path, mode="rb") as test_data:
        results = predictor.predict_image(project.id, test_data, iteration_id)
    prediction_dict={}
    # Display the results.
    for prediction in results.predictions:
        prediction_dict[prediction.tag_name]=prediction.probability * 100
        print ("\t" + prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100))
    status=max(prediction_dict, key=prediction_dict.get)
    max_value=max(prediction_dict.values())
    return status,max_value


if __name__=='__main__':
    print(test_with_file_data('./test_new_1005/13.jpeg'))