import numpy as np
import tensorflow as tf
import random
from scipy.ndimage import imread
from shutil import copyfile, copy2

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

#load sample images
# #TODO:
# #   - Get list of all file names
import glob

training = False
tf.set_random_seed(1221)
def call_nn(input_folder, model_folder, output_folder, training=False):
    if training == True:
        file_list = glob.glob("TrainingSetRotations/*.png") #here you insert the name of the folder where the training set is stored
        # #   - loop over the file name list and append to dataset array
        dim = 80 #modified input file dimensions
        dataset = np.zeros(shape = (len(file_list), dim, dim, 3), dtype = np.float32)
        labels_data = np.zeros(shape = (len(file_list), 2), dtype = np.float32)


        good_ids = []
        bad_ids = []
        for i, file_name in enumerate(file_list):
            dataset[i,:,:,:] = imread(file_name, mode="RGB")
            file_name_split = file_name.split(".")
            if file_name_split[-2].endswith('A'):
                THE_LABEL_WE_JUST_FOUND = np.array([1,0],dtype = np.float32) #this means flake is good
                good_ids.append(i)
            else:
                THE_LABEL_WE_JUST_FOUND = np.array([0,1],dtype = np.float32)
                bad_ids.append(i)
            #   - load label for corresponding image and append to labels_training array
            #     HOW DO I GET THE LABELS? = [0,1] or [1,0]
            labels_data[i,:] = THE_LABEL_WE_JUST_FOUND

        total = len(file_list)
        nr_eval = int(len(good_ids)*0.01)

        eval_ids = random.sample(good_ids, nr_eval) + random.sample(bad_ids, nr_eval)
        labels_eval = labels_data[eval_ids]
        print(labels_eval)
        dataset_eval = dataset[eval_ids,:,:,:]

        #eval_ids = random.sample(list(range(len(good_ids))), nr_eval) #now the eval set has 10% of good flakes and nothing else
        #eval_ids = random.sample(list(range(len(bad_ids))), nr_eval) #now the eval set has only bad flakes (count is equal to 20% of good flakes)
        good_training_ids = [i for i in range(total) if i in good_ids and i not in eval_ids]
        bad_training_ids = [i for i in range(total) if i in bad_ids and i not in eval_ids]
        training_ids = [i for i in range(total) if i not in eval_ids]

        labels_training = labels_data[training_ids]
        dataset_training = dataset[training_ids,:,:,:]

        print(np.shape(dataset))
        # labels_training = np.array([[1,0],[1,0],[0,1]], dtype = np.float32)
        print(np.shape(labels_training))

        training_size, height, width, channels = dataset_training.shape
    else:

        file_list = glob.glob("{}/*.png".format(input_folder)) #here you insert the name of the folder
        #where the pre-processed images ready for flake search are stored
        # #   - loop over the file name list and append to dataset array
        dim_test = 80 #modified input file dimensions
        test_dataset = np.zeros(shape = (len(file_list), dim_test, dim_test, 3), dtype = np.float32)
        test_labels = np.zeros(shape = (len(file_list), 2), dtype = np.float32)

        for i, file_name in enumerate(file_list):
            test_dataset[i,:,:,:] = imread(file_name, mode="RGB")


        nr_test_flakes, height, width, channels = test_dataset.shape

    learning_rate = 0.0000005

    #create the graph with input X plus a convolutional layer applying two filters
    X = tf.placeholder(tf.float32,shape=(None, height, width, channels))
    labels = tf.placeholder(tf.float32, shape= (None, 2))

    conv = tf.layers.conv2d(X, filters = 64, kernel_size = 5, strides = [2,2], padding = "SAME",activation=tf.nn.relu)
    max_pool = tf.nn.max_pool(conv, ksize=[1,2,2,1], strides=[1,2,2,1],padding = "VALID")
    conv2 = tf.layers.conv2d(max_pool, filters = 64, kernel_size = 3, strides = [1,1], padding = "SAME",activation=tf.nn.relu)
    max_pool2 = tf.nn.max_pool(conv2, ksize=[1,2,2,1], strides=[1,2,2,1],padding = "VALID")
    conv3 = tf.layers.conv2d(max_pool2, filters = 128, kernel_size = 3, strides = [1,1], padding = "SAME",activation=tf.nn.relu)
    max_pool3 = tf.nn.max_pool(conv3, ksize=[1,2,2,1], strides=[1,2,2,1],padding = "VALID")
    conv4 = tf.layers.conv2d(max_pool3, filters = 256, kernel_size = 3, strides = [1,1], padding = "SAME",activation=tf.nn.relu)
    max_pool4 = tf.nn.max_pool(conv4, ksize=[1,2,2,1], strides=[1,2,2,1],padding = "VALID")
    #conv5 = tf.layers.conv2d(max_pool4, filters = 256, kernel_size = 2, strides = [1,1], padding = "SAME",activation=tf.nn.relu)
    #max_pool5 = tf.nn.max_pool(conv5, ksize=[1,2,2,1], strides=[1,2,2,1],padding = "VALID")

    reshaped = tf.contrib.layers.flatten(max_pool4)

    dense = tf.layers.dense(inputs=reshaped, units=256, activation=tf.nn.relu)

    # Add dropout operation; 0.6 probability that element will be kept
    dropout = tf.layers.dropout(inputs=dense, rate=0.5, training=training)

    logits = tf.layers.dense(inputs=dropout, units = 2, activation = None)
    outputs = tf.sigmoid(logits)
    xentropy = tf.losses.softmax_cross_entropy(onehot_labels = labels, logits = logits)

    # your class weights
    #class_weights_1 = tf.constant([[2.0, 1.0]])
    #class_weights_2 = tf.constant([[1.0, 2.0]])

    # deduce weights for batch samples based on their true label
    #weights_1 = tf.reduce_sum(class_weights_1 * labels, axis=1)
    #weights_2 = tf.reduce_sum(class_weights_2 * labels, axis=1)

    # compute your (unweighted) softmax cross entropy loss
    #unweighted_xentropy = tf.losses.softmax_cross_entropy(onehot_labels = labels, logits = logits)

    # apply the weights, relying on broadcasting of the multiplication
    #weighted_xentropy_1 = unweighted_xentropy * weights_1
    #weighted_xentropy_2 = unweighted_xentropy * weights_2

    # reduce the result to get your final loss
    #xentropy = tf.reduce_mean(weighted_xentropy_1)

    loss = xentropy
    accuracy = tf.metrics.accuracy(labels = labels, predictions = outputs)
    accuracy, accuracy_op = tf.metrics.accuracy(labels=tf.argmax(labels, 1),
                                      predictions=tf.argmax(outputs,1))
    optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate)
    training_op = optimizer.minimize(loss)
    #training_op = optimizer.minimize(loss)

    # Create Summary
    loss_train_summary = tf.summary.scalar('loss_train', loss)
    test_writer = tf.summary.FileWriter('flakes/')

    loss_eval_summary = tf.summary.scalar('loss_eval', loss)

    #dummy = tf.Variable(0)


    # init = tf.global_variables_initializer()
    init = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
    saver = tf.train.Saver()

    sess = tf.Session()

    # This may be redudant to got some errors that I didnt understand:



    if training:
        sess.run(init)

        #loop over the training eval_steps
        steps = 120000
        eval_steps = 5000


        # We make history
        history = {}
        history['loss'] = np.zeros(steps)
        history['accuracy_train'] = np.zeros(steps)
        history['loss_eval'] = np.zeros(int(steps/eval_steps))
        history['step_eval'] = np.zeros(int(steps/eval_steps))
        history['accuracy'] = np.zeros(int(steps/eval_steps))

        nr_batch = int(len(good_training_ids)*0.01)

        step_eval = 0

        for step in range(steps):

            batch_ids = random.sample(good_training_ids, nr_batch) + random.sample(bad_training_ids, nr_batch)
            #print(nr_batch)
            #print(batch_ids)
            labels_batch = labels_data[batch_ids]
            training_batch = dataset[batch_ids,:,:,:]

            _, loss_val, summary = sess.run([training_op, loss, loss_train_summary], feed_dict={X:training_batch, labels:labels_batch})
            # print('Training Loss is at: ')
            # print(loss_val)
            history['loss'][step] = loss_val

            train_accuracy, _ = sess.run([accuracy, accuracy_op], feed_dict={X: training_batch, labels: labels_batch})
            train_accuracy = sess.run([accuracy], feed_dict={X: training_batch, labels: labels_batch})
            history['accuracy_train'][step] = train_accuracy[0]

    #        _, loss_val, summary = sess.run([training_op2, loss, loss_train_summary], feed_dict={X:training_batch, labels:labels_batch})
    #        # print('Training Loss is at: ')
    #        # print(loss_val)
    #        history['loss'][step] = loss_val


            if step % eval_steps == 0:
                loss_eval, summary_eval = sess.run([loss, loss_eval_summary], feed_dict={X: dataset_eval, labels: labels_eval})
                print('Evaluation loss is at:')
                print(loss_eval)
                history['loss_eval'][step_eval] = loss_eval
                history['step_eval'][step_eval] = step
                eval_accuracy, _ = sess.run([accuracy, accuracy_op], feed_dict={X: dataset_eval, labels: labels_eval})
                eval_accuracy = sess.run([accuracy], feed_dict={X: dataset_eval, labels: labels_eval})
                print('Accuracy is at:')
                print(eval_accuracy)
                history['accuracy'][step_eval] = eval_accuracy[0]
                step_eval = step_eval + 1
                #sess.run(dummy.assign(step_eval))
                test_writer.add_summary(summary_eval, step)
                #add max_to_keep argument to increase number of saved check-points
                saver.save(sess, 'flakes/', global_step=step, max_to_keep = 24)
                test_writer.add_summary(summary, step)

        #output = sess.run(conv, feed_dict={X: dataset})
        #plt.imshow(output[0, :, :, 1], cmap = "gray") #plot 1st image's second feature map
        #plt.savefig("1stImage_2ndFeature.pdf")

        #save the data
        #np.savetxt("train_loss.txt", loss)
        #np.savetxt("eval_loss.txt", loss_eval)
        plt.figure()
        plt.plot(history['loss'],'.-',label='Training Loss');
        plt.plot(history['step_eval'], history['loss_eval'],'*-', label = 'Validation Loss')
        plt.xlabel("Learning Step")
        plt.ylabel("Loss")
        plt.savefig("loss.pdf")

        plt.figure()
        plt.plot(history['accuracy_train'],'.-',label='Training Accuracy');
        plt.plot(history['step_eval'], history['accuracy'],'*-', label = 'Accuracy')
        plt.xlabel("Learning Step")
        plt.ylabel("Accuracy")
        plt.savefig("accuracy.pdf")
    else:
        tf.reset_default_graph()
        ### APPLY MODEL ON RAW DATA ###

        saver.restore(sess, "{}/-119000".format(model_folder))
        #print(sess.run(dummy))
        test_labels = sess.run(outputs , feed_dict={X: test_dataset})
        good_ones = 0
        for i in range(nr_test_flakes):
            if test_labels[i,0] > 0.6:
                print('This flake is good: ' + file_list[i])
                copy2(file_list[i], "{}/".format(output_folder))
                good_ones += 1
        print(str(good_ones) + ' good files found')
