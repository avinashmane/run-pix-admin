import pandas as pd
import gspread

skipcols=['ticketAndDiscountList','answerList']

def update_tab(gs,df_reg):

  df_=df_reg.copy()
  df_['Status']='SUCCESS'

  "remove skipcol columns"
  for c in skipcols :#df_.columns:
    if c in df_:
      del(df_[c])

  # keep old rows with unique registrationId
  try:
    newKeys=df_['registrationId'].values
    df_deleted=pd.DataFrame(gs.get_all_records()
                ).query(f"registrationId not in @newKeys").copy()
    # df_deleted.loc[:,'userName']='CANCELLED|'+df_deleted.userName
    df_deleted['Status']='CANCELLED?'
    # df_x=df_.append(df_deleted,   ##Sep23 append removed
    df_x = pd.concat([df_, df_deleted], 
                  ignore_index=True,
                  verify_integrity=True )
  except Exception as e:
    print (f"Error {e!r}")
    df_x=df_

  "new dataframe with header"
  df_x=pd.concat([pd.DataFrame([
                df_x.columns],columns=df_x.columns),
                df_x],
              ignore_index=True)

  gs.batch_update([{
      'range': 'A1:'+gspread.utils.rowcol_to_a1(*df_x.shape),
      'values': df_x.fillna('').values.tolist()}
  ])


def subDict_ans(dat,subdict,keys):
  a_=[]
  for x in dat:
    dict_={k:x[k] for k in keys}
    for a in x[subdict]:
      # for k in keys:
      try:
        dict_[a['question']]=a['answer']
      except Exception as e:
        print (f"Error: {a!r}{e!r}")
        raise
    a_.append(dict_)
  return a_

def subDict_tkt(dat,subdict,keys):
  a_=[]
  for i,x in enumerate(dat):
    i
    tickets=x[subdict]
    for t in tickets:
      for k in keys:
        if k in x.keys():
          t[k]=x[k]
        else:
          for val in [y['answer'] for y in x['answerList'] if k == y['question']]:
            t[k]=val
            break
          else:
            t[k]=''
          # print(i,x['registrationId'],k)
      a_.append(t)
  return a_
