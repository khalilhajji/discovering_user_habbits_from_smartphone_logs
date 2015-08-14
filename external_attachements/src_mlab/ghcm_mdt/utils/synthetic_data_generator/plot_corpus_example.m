addpath('./utils/synthetic_data_generator/')

FILENAME = 'tmp.mat';
ALPHA = 0.1;
BETA = 0.1;
Nd = 20;
N_DOCS = 15;
N_TOPICS = 3;
VOC_SIZE = 5;

generate_synthetic_dataset(FILENAME, ALPHA, BETA, Nd, N_DOCS, N_TOPICS, VOC_SIZE);

% Plot the dataset and display phi and theta
load(FILENAME)
phi
theta
plot_corpus(docs_vector, words_vector, topics_vector)

delete(FILENAME)
