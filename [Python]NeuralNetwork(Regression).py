#datasets link : https://www.kaggle.com/rodolfomendes/abalone-dataset

#신경망 연산에 필요한 필수 모듈 불러오기
import numpy as np
import csv

#난수값을 고정시켜주기 위한 seed (같은 조건에서 실험을 위한 장치)
np.random.seed(107)

#하이퍼파라미터값 설정하기
RND_MEAN      = 0
RND_STD       = 0.0030

LEARNING_RATE = 0.001

#메인함수 정의하기 (함수를 정의하는 과정에서 이렇게 값을 설정해주게 되면 이후에 따로 값을 설정하지 않아도 기본으로 값이 설정됨.)
#다만 함수를 호출하는 과정에서 수정도 얼마든지 가능
def main_exec(epoch_count = 10, mb_size = 10, report = 1, train_rate = 0.8):
    load_dataset()                                            #데이터를 불러오는 함수
    init_model()                                              #파라미터를 초기화 해주는 함수
    train_and_test(epoch_count, mb_size, report, train_rate)  #데이터를 분할하고 학습과 테스트를 수행하는 함수

#데이터를 불러오고 버퍼(임시공간)와 원-핫 인코딩을 처리하는 함수
def load_dataset():
    with open("./AI/datasets/abalone.csv") as csvfile:           #프로젝트내의 데이터를 with open()을 통해 불러오는 과정
        csvreader = csv.reader(csvfile)            #불러온 데이터를 파이썬 내부로 읽어들이는 과정 / csv.reader()
        next(csvreader, None)                      #데이터의 첫 번째 행은 변수명이기 때문에 next()를 통해 건너뛰는 과정
        rows      = []                             #for 반복문과 append()를 활용하여 csvreader 데이터를 한줄씩 읽어오고
                                                   #빈 리스트인 rows를 생성하여 저장(이렇게 미리 생성해야 저장이 됩니다.)
        for row in csvreader:                       #반복문을 활용하여 데이터를 읽어오는 과정
           rows.append(row)

    global data, input_cnt, output_cnt             #전역번수를 설정하는 과정. data       → 임시공간 이후 원-핫 인코딩 처리된 데이터.
                                                   #                       input_cnt  → 독립변수의 수(10)
                                                   #                       output_cnt → 종속변수의 수(1)
    input_cnt, output_cnt = 10, 1                  #이러한 방식으로 코드를 작성할 수 도 있다.(직관적)
    data = np.zeros([len(rows), input_cnt + output_cnt])     #데이터를 원-핫 인코딩 처리하기 위한 임시공간(버퍼)를 생성하는 과정
                                                             #np.zeros()를 활용하여 전체 데이터의 행과 열을 인자로 넣어주기 위해
                                                             #데이터의 행은 len(), 데이터의 열은 input_cnt, output_cnt의 합으로.
    for n, row in enumerate(rows):                 #enumerate()를 활용하여 반복문을 수행 ※enumerate() 활용방법 숙지
                                                   #데이터를 한줄 씩 받아와 조건문을 통해 원-핫 인코딩을 수행하는 과정(세 조건에 합당한 위치로 1값을 할당.)
        if row[0] == 'I' : data[n, 0] = 1          #만약(if) row로 전달된 행의 첫 번째(0) 값이 'I' 라면은 : 버퍼로 만든 data[0,0]의 위치에 1값을 할당.
        if row[0] == 'M' : data[n, 1] = 1          #만약(if) row로 전달된 행의 첫 번째(0) 값이 'M' 라면은 : 버퍼로 만든 data[0,1]의 위치에 1값을 할당
        if row[0] == 'F' : data[n, 2] = 1          #만약(if) row로 전달된 행의 첫 번째(0) 값이 'F' 라면은 : 버퍼로 만든 data[0,2]의 위치에 1값을 할당
        data[n, 3:] = row[1: ]                     #문자열 데이터에 대한 인코딩이 끝났다면은, row에 저장된 [1: ]에 값들(2 ~ 8번째 독립변수 데이터)을
                                                   #data[0, 3: ]의 위치로 저장하라(원-핫 인코딩 위치 이후). ※범주가 3개(I,M,F) 이기에 4번째 위치부터 값을 할당.
                                                   #이 과정을 통해 전체 데이터(4177)를 반복문을 통해 원-핫 인코딩 처리를 수행합니다.

#가중치와 편향을 초기화 하는 함수
def init_model():
    global weight, bias, input_cnt, output_cnt           #전역변수를 설정합니다. 가중치 / 편향 / input_cnt / output_cnt
    weight = np.random.normal(RND_MEAN,                  #normal()를 활용하여 가중치에 대한 초기 무작위 값을 설정합니다. ( 평균, 표준편차, 크기[10,1] )
                              RND_STD,
                              [input_cnt, output_cnt])
    bias   = np.zeros([output_cnt])                      #zeros()를 활용하여 편향에 대한 초기 무작위 값을 설정합니다. (크기[1])
                                                         #※편향의 경우 초기에 값을 너무 크게 주면 학습에 영향을 주기에 np.zeros()를 활용하였다.

#학습용, 테스트용 데이터 분할과 학습 및 테스트를 수행하는 함수
def train_and_test(epoch_count, mb_size, report, train_rate):    #메인함수에서 기본값으로 설정한 4개의 인자값들을 받아옵니다.(기본값 : 10, 10, 1, 0.8)
    step_count = arrange_data(mb_size, train_rate)               #arrange_data()은 step_count, 즉 1 epoch 와 mb_size값 에 맞춰 1 epoch에 따른 미니배치 개수를 반환
    test_x, test_y = get_test_data()                             #get_test_data()는 전체 데이터에서 테스트 데이터를 독립변수(test_x)와 종속변수(test_y)로 나눠 반환

                                                            #2중 반복문이 수행됩니다. 첫 반복문은 epoch_count로 설정한 값을 바탕으로 반복문 수행합니다.
    for epoch in range(epoch_count):
        losses, accs = [], []                               #1epoch가 수행될 때 마다 반환되는 loss, acc를 append()를 활용하여 losses, accs로 저장합니다. (※빈 리스트 필요)

        for n in range(step_count):                         #두 번째 반복문이 수행되는 기준은 1 epoch_count에 따른 step_count를 기준으로 반복문이 수행.
            train_x, train_y = get_train_data(mb_size, n)   #get_train_data()에서는 mb_size과 반복문에 따른 n을 인자로 받아 train_x와 train_y를 전달받습니다.
            loss, acc        = run_train(train_x, train_y)  #학습을 수행하는 run_train()는 학습 데이터를 받아 학습데이터에 따른 손실(loss)과 정확도(acc)를 반환합니다.
            losses.append(loss)                             #append()를 활용하여 학습 데이터를 활용한 미니배치 단위로 수행된 학습 결과에 따른 손실을 losses에 저장.
            accs.append(acc)                                #append()를 활용하여 학습 데이터를 활용한 미니배치 단위로 수행된 학습 결과에 따른 정확도를 accs에 저장.
                                                            #1epoch수행을 위한 모든 미니배치 단위의 학습이 종료.
        if report > 0 and (epoch+1) % report == 0:          #학습 중간 결과를 출력하는 과정. 모든 출력 결과를 출력하기 보다는
                                                            #우리가 설정한 주기(report)만큼 출력을 하기 위한 조건문과 연산을 활용한 출력 방식.(※ % 연산자 동작방식 확인)
            acc = run_test(test_x, test_y)                  #위의 조건에 부합하면 테스트 데이터를 활용하여 acc를 연산하고 반환
            print("Epoch {} : Train - loss = {:5.3f}, accuracy = {:5.3f} / Test = {:5.3f}".\
                  format(epoch + 1, np.mean(losses), np.mean(accs), acc))                         #format()을 활용한 중간 연산결과 출력. {:5.3f}는 값을 확보 및
                                                                                                  #출력 범위를 지정
                                                                                                  #1epoch당 미니배치 단위의 정확도와 손실에 대하여 평균을 구해준다.
                                                                                                  #맨 마지막의 acc의 경우 테스트 데이터를 활용한 결과로서 값을 출력.
    final_acc = run_test(test_x, test_y)                    #최종결과에 대하여 한 번더 출력하기 위한 코드
    print("\n 최종 테스트 : Final accuracy = {:5.3f}".format(final_acc))
                                                            #\n의 경우 출력을 수행할 때 한 줄을 띄워 출력하는 코드다.

#우리가 설정한 mb_size에 맞게 1epoch에 대한 미니배치 스텝 수(step_count)를 반환하는 함수
def arrange_data(mb_size, train_rate):                      #train_and_test()에서 받은 mb_size와 train_rate를 인자로 받는다.
            global data, shuffle_map, test_begin_index      #전역변수를 설정한다. 원-핫 인코딩 된 데이터, 무작위로 섞인 shuffle_map, 학습 데이터와 테스트 데이터의 경계선.
            shuffle_map = np.arange(data.shape[0])          #전체 데이터의 첫 번째 속성값을 np.arange()로 받아 shuffle_map으로 저장한다. (지금까지는 일반적인 순서)
            np.random.shuffle(shuffle_map)                  #np.random.shuffle()을 활용하면 인덱스가 무작위로 섞이게 됩니다.

            step_count = int(data.shape[0] * train_rate) // mb_size #★학습 데이터 비율(train_rate)를 통해 전체 데이터에서 학습 데이터 수를 곱해준 다음
                                                                    #mb_size로 나눠(//) 그 값을 step_count에 저장한다. 1에폭에 대한 미니배치가 얼마나 생성되는지 알 수 있음.
            test_begin_index = step_count * mb_size         #step_count와 mb_size를 곱해 학습 데이터와 테스트 데이터에 대한 경계선 인덱스(위치)를 구해준다.
                                                            #이렇게 구해진 test_begin_index값은 전역변수로 하여 다른 함수에서도 활용할 수 있게된다.
            return step_count

#함수 명 그대로 테스트 데이터를 얻어내는 과정이다.train_and_test()가 수행될 때 두 번째로 수행되는 함수.
def get_test_data():
    global data, shuffle_map, test_begin_index, output_cnt  #전역변수로는 위에서 모두 구한 변수들을 가져온다.
    test_data = data[shuffle_map[test_begin_index:]]        #data에 접근하여[전체 인덱스를 가져오고[학습과 테스트 데이터 경계선 부터 : 끝까지]] 값을 test_data에 할당한다.
    return test_data[ : , : -output_cnt], test_data[ : , -output_cnt : ]    #반환되는 값은 test_x, test_y다. 이를 test_data를 슬라이싱하여 행은 전부 다 가져오고,
                                                                            #열(변수)은 -output_cnt 를 활용하여 할당된 범위로 변수를 가져옵니다.
                                                                            #(※ 슬라이싱 기법에서 - 를 활용하는 방식 숙지하기.)

#함수 명 그대로 학습 데이터를 얻어내는 과정이다.
def get_train_data(mb_size, nth):                          #nth란 train_and_test()에서 2중 반복문 수행하여 발생한 n과 같습니다.
                                                           #n은 1epoch당 미니배치 스텝 수를 0부터 차례대로 반복하여 들어오게 되는 값입니다. (※ train_and_test() 참고)
    global data, shuffle_map, test_begin_index, output_cnt #전역변수 설정
    if nth == 0 :                                          #nth가 0인 경우 즉,1epoch가 수행될 때 첫 번째 미니배치 단위로서, epoch이 순차적으로 수행될 때마다 가장 처음에 수행.
        np.random.shuffle(shuffle_map[:test_begin_index])  #위의 조건문에 부합하면 전체 데이터셋에서[ 처음부터 : 테스트 데이터 경계선까지] 즉, 학습 데이터 부분만을 섞어줍니다.
                                                           #이렇게 매번 에폭이 늘어날 때마다 학습 데이터를 섞어주게 되면 학습에 대한 효율성이 증가하여 긍정적인 영향을 미친다.
    train_data = data[shuffle_map[ mb_size * nth : mb_size * (nth + 1)]]
                                                           #전체 데이터에서 학습 데이터를 미니배치 크기(mb_size)단위로 분할하는 과정입니다.
                                                           #nth는 0 부터 미니배치 단위만큼 반복적으로 값이 들어오기 때문에 결과적으로 mb_size로 설정한 값에 따라
                                                           #학습 데이터가 미니배치 단위로 분할됩니다. mb_size가 0이라면 (0 : 10, 10 : 20, 20 : 30, ... )
    return train_data[ : , : -output_cnt], train_data[ : , -output_cnt : ]
                                                           #이 과정은 테스트 데이터를 종속변수와 독립변수로 분할하는 과정과 동일합니다. (※ 슬라이싱 기법 숙지)

#학습을 수행하는 함수입니다.
def run_train(x,y):                                      #x,y는 train_x와 train_y를 입력으로 받습니다.
            output, aux_nn = forward_neuralnet(x)        #신경망의 퍼셉트론 연산 방식인 f_θ(x) = θ_0 + θ_0*x 가 수행되는 함수입니다. 결과로 반환되는 값은 예측값이며,
                                                         #aux_nn의 경우 역전파를 수행할 때 활용되는 보조정보입니다.(nn은 neuralnet의 약자, nn은 입력값인 x를 그대로 반환)
            loss, aux_pp   = forward_postproc(output, y) #mse에 따른 손실(loss)를 반환하는 메서드로 마찬가지로 역전파를 수행하는데 있어 보조정보인 aux_pp를 반환합니다.
                                                         #(pp는 postproc의 약자입니다. aux_pp는 예측값과 실제값의 편차인 diff를 반환합니다.)
            accuracy = eval_accuracy(output, y)          #예측값(output)과 실제값(y)를 활용하여 정확도를 구해 반환하는 함수 입니다.

            G_loss = 1.0                                 #역전파를 수행하는 첫 번째 단계입니다. 이 값은 우리가 구한 loss에 대한 즉 손실에 대한 기울기값이며 1의 값을 갖습니다.
            G_output = backprop_postproc(G_loss, aux_pp) #역전파를 수행하는 과정은 합성함수의 편미분 과정입니다. 이 과정에 대한 수식을 나타내며, 경사하강법에서 학습률과
                                                         #곱해지는 부분에 대한 결과를 반환합니다. (※ G는 기울기의 약자)
            backprop_neuralnet(G_output, aux_nn)         #앞서 구한 G_output과 aux_nn(입력 데이터 x)를 활용하여 θ를 갱신하는 메서드입니다.
            return loss, accuracy                        #1회 학습한 결과인 손실(loss)과 정확도(accuracy)를 반환합니다.
                                                         #run_train()은 미니배치 단위인 step_count 수 만큼 반복해서 학습을 수행합니다.
                                                         #그래서 각 구해진 loss와 accuracy는 append()를 통해 losses, accs에 저장됩니다.

def run_test(x,y):                                       #x,y는 test_x와 train_y를 입력으로 받습니다.
    output, _ = forward_neuralnet(x)                     #마찬가지로 예측값을 반환하지만 테스트를 수행하는 만큼 보조정보는 더 이상 필요없습니다. 이러한 경우 "_" 처리합니다.
    accuracy  = eval_accuracy(output, y)                 #마찬가지로 테스트 데이터를 활용한 정확도를 추출합니다.
    return accuracy                                      #추출된 값은 반환되어 집니다.

#-----------------------------------------------------------------------------------------------------------------------------------------------

def forward_neuralnet(x):                                #신경망 연산을 수행하는 과정입니다.
    global weight, bias                                  #앞에서 초기화하여 진행한 가중치와 편향을 전역변수로 설정합니다.
    output = np.matmul(x, weight) + bias                 #행렬곱을 수행하는 np.matmul()을 활용하여 입력값과 가중치를 연산하고, 편향을 더해줌으로 output(예측)을 계산합니다.
    return output, x                                     #x는 aux_nn으로 이후에 역전파를 위해 활용되어 집니다.

#손실함수를 구하는 과정을 단계별로 구분하여 함수 구축.(사용되는 손실함수 = mse)
def forward_postproc(output,y):                          #예측값(output)과 실제값(y)를 전달받는다.
    diff    = output - y                                 #1단계 : 예측값에서 실제값에 대한 편차를 구한다.
    square  = np.square(diff)                            #2단계 : np.square()를 활용하여 제곱을 구한다.
    loss    = np.mean(square)                            #3단계 : np.mean()을 활용하여 평균을 구한다.
    return loss, diff                                #loss와 diff를 반환하는데, diff는 이후 aux_pp로 활용되며 역전파 과정에서 사용됩니다.

#실질적인 파라미터 갱신이 이뤄지는 함수입니다.
def backprop_neuralnet(G_output, x):                     #G_output과 x를 받아줍니다. G_output은 θL/θY 를 의미하며, x는 aux_nn을 받아주는데, 입력값 x와 같습니다.
    global weight, bias                                  #전역변수로 가중치와 편향을 받아와줍니다.
    g_output_w = x.transpose()                           #G_w(θL/θW)를 구하기 위해서는 결과적으로 X^T * G 를 연산해야 합니다.
                                                         #그래서 입력값 X를 받아와 전치(.transpose())시켜주는 과정입니다.

    G_w = np.matmul(g_output_w, G_output)                #가중치 갱신을 위한 (θL/θY * θY/θW) 를 구하는 과정입니다.
    G_b = np.sum(G_output, axis = 0)                     #편향 갱신을 위한 (θL/θY * θY/θB) 를 구하는 과정입니다. (※ axis = 0 는 행을 따라 동작합니다.)

    weight -= LEARNING_RATE * G_w                        #위에서 구한 합성함수의 미분 결과에 학습률(η)을 곱하고 기존 가중치에서 빼줌으로 가중치가 갱신(학습)되는 과정입니다. 
    bias -= LEARNING_RATE * G_b                          #위에서 구한 합성함수의 미분 결과에 학습률(η)을 곱하고 기존 편향에서 빼줌으로 편향이 갱신(학습)되는 과정입니다.

def backprop_postproc(G_loss, diff):                     #mse에 대한 역전파 과정을 수식으로 재현한 코드입니다.
    shape = diff.shape                                   #mse의 과정 중 제곱에 관한 손실(평균)의 미분을 구하는 과정에서 손실은 [미니배치 크기, 출력벡터 크기] 즉,
                                                         #[N,M]의 크기를 갖고 있기에 diff의 shape 속성을 활용하여 [N,M]의 크기를 추출해 줍니다.

    G_loss = 1.0                                         #mse에 영향을 미친 모든 성분에 대하여 미분을 구하기 위해 각 단계별로 연쇄법칙을 적용하여
                                                         #수식을 작성하게 되면 θL/θmse 즉, θL/θL을 구할 수 있는데, 이는 당연하게도 1의 값을 갖습니다.
                                                         #결과적으로 이 단계의 결과를 G_loss라 하고 1의 값을 할당합니다.

    g_loss_square = np.ones(shape) / np.prod(shape)      #θL/θsquare를 구하는 과정입니다. 이는 1/MN이라는 값을 얻게되는데, 이 과정에서 np.ones()와 np.prod()를 활용합니다.
    g_square_diff = 2 * diff                             #θsquare/θdiff를 구하는 과정입니다. 이는 결국 2diff라는 결과를 얻을 수 있으며, 2*diff 코드로 재현할 수 있습니다.
    g_diff_output = 1                                    #θdiff/θoutput을 구하는 과정입니다. 이 또한 결국 1 이라는 결과값을 얻게되기에, 단순 1로 재현하였습니다.

    G_square = g_loss_square * G_loss                    #θL/θoutput을 최종적으로 구하기 위한 연쇄법칙을 적용한 결과값을 연산하기 위해
    G_diff = g_square_diff * G_square                    #위에서 구한 G_loss 부터 시작하여 g_diff_output까지 순차적으로 곱하여 값을 연산하는 과정입니다.
    G_output = g_diff_output * G_diff

    return G_output                                      #이렇게 구한 값은 G_output(θL/θoutput)으로 각 가중치와 편향의 갱신에 활용되어집니다.

def eval_accuracy(output, y):                            #오류율을 연산하는 수식을 함수로 구현하였습니다.
    mdiff = np.mean(np.abs((output - y)/y))              #예측값과 실제값의 편차를 실제값으로 나누며, 이 값에 대한 절대값을 적용하여 줍니다.
    return 1 - mdiff                                   #실질적인 정확도를 확인하기 위해 1에서 값을 빼어 결과를 출력하여 주겠습니다.

main_exec()