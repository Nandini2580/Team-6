import pandas as pd
import numpy as np
import random
import joblib
from datetime import datetime, timedelta

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# ======================
# DATA GENERATION
# ======================

stations=["VSKP","BZA","RNC","NAGP","DURG"]

rake_capacity={

"BOXN":3800,
"BCN":2600,
"BTPN":3000

}

data=[]

start_date=datetime(2024,1,1)

for i in range(1200):

    date=start_date+timedelta(days=i)

    station=random.choice(stations)

    load=random.randint(1000,10000)

    capacity=random.choice(list(rake_capacity.values()))

    rakes=int(np.ceil(load/capacity))

    data.append([

    station,
    date.month,
    date.day,
    load,
    rakes

    ])


df=pd.DataFrame(data,columns=[

"station",
"month",
"day",
"load",
"rakes"

])


# ======================
# ENCODING
# ======================

df=pd.get_dummies(df,columns=["station"])

X=df.drop("rakes",axis=1)

y=df["rakes"]


# Save feature columns
joblib.dump(X.columns.tolist(),"models/feature_columns.pkl")


# ======================
# SCALING
# ======================

scalerX=MinMaxScaler()
scalerY=MinMaxScaler()

X_scaled=scalerX.fit_transform(X)

y_scaled=scalerY.fit_transform(y.values.reshape(-1,1))


joblib.dump(scalerX,"models/scaler_X.pkl")
joblib.dump(scalerY,"models/scaler_Y.pkl")


# ======================
# SEQUENCE CREATION
# ======================

SEQ=1

X_seq=[]
y_seq=[]

for i in range(len(X_scaled)-SEQ):

    X_seq.append(X_scaled[i:i+SEQ])

    y_seq.append(y_scaled[i+SEQ])

X_seq=np.array(X_seq)
y_seq=np.array(y_seq)


# ======================
# LSTM MODEL
# ======================

model=Sequential()

model.add(LSTM(50,input_shape=(SEQ,X_seq.shape[2])))

model.add(Dense(1))


model.compile(

optimizer="adam",
loss="mse"

)

model.fit(

X_seq,
y_seq,
epochs=30,
batch_size=32

)


model.save("models/forcasting.h5")

print("LSTM Model Trained")