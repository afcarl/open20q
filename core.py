    # According to the ideas of http://lists.canonical.org/pipermail/kragen-tol/2010-March/000912.html
                
    import numpy
    items = ["1","2","3","4","5","6","7","8","9","0"]
    a_priori_Ps = numpy.ones(len(items))/len(items)
    questions = ["Is X=%s?"%item for item in items] + ["X<=5?", "Is X>5?", "Is X odd?", "Is X even?", "Is X<=1?", "Is X<=7?", "Is X close to 5?", "Is X prime?"]
    
    P_Q_given_X = numpy.vstack((numpy.eye(len(items)), numpy.array(
        [[1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
         [0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
         [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
         [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 1, 1, 1, 1, 1, 1, 0, 0, 1],
         [0,.1,.8, 1,.9, 1,.8,.1, 0, 0],
         [0, 1, 1, 0, 1, 0, 1, 0, 0, 0],
         ])))
    
    def xlogx(x):
       x = numpy.asarray(x)
       l = numpy.zeros_like(x)
       l[x>0] = numpy.log(x[x>0])
       return x * l
    
    def entropy(Ps):
        Ps = numpy.asarray(Ps)
        Ps = Ps / sum(Ps)
        Ps[numpy.isnan(Ps)] = 0
        l = numpy.zeros_like(Ps)
        l[Ps>0] = numpy.log(Ps[Ps>0])
        return -sum(Ps*l)
    
    def bayes(P_X_given_Y, P_Y, P_X):
        P_X = P_X.view().reshape((-1, 1))
        P_Y_given_X = ((P_X_given_Y*P_Y)/P_X).transpose()
        P_Y_given_X[numpy.isnan(P_Y_given_X)]=0
        return P_Y_given_X
    
    def entropy_after_answer(P_Q, P_XQ, P_XnotQ):
        entropies = P_Q * entropy(P_XQ) + (1-P_Q) * entropy(P_XnotQ)
        entropies[P_Q == 0] = numpy.inf 
        entropies[P_Q == 1] = numpy.inf 
        return entropies 
    
    n=50
    def update(answers, item):
        global P_Q_given_X
        global a_priori_Ps
        global n
        P_Q_given_X[answers!=0.5][:, item] = (n-1.)/n*P_Q_given_X[answers!=0.5][:, item] + answers[answers!=0.5]/n
        a_priori_Ps *= (n-1)/float(n)
        a_priori_Ps[item] += 1./n
    
    def add_item(answers, item):
        global P_Q_given_X
        global items
        global a_priori_Ps
        i = len(items)
        X = numpy.hstack((1, numpy.zeros(i), answers[i:]))
        X.shape = (-1, 1)
        P_Q_given_X = numpy.hstack((X, numpy.vstack((numpy.zeros(i), P_Q_given_X))))
        items.insert(0, item)
        questions.insert(0, ("Is X=%s?" % item))
        a_priori_Ps = numpy.hstack((1./n, (n-1.)/n*a_priori_Ps))
        
    epsilon = 0.1
    def guess():
        P_X = a_priori_Ps/sum(a_priori_Ps)
        answers = numpy.ones(len(questions))*0.5
        counter = 0
        for counter in xrange(4):
            P_Q = numpy.dot(P_Q_given_X, P_X)
            P_XQ = bayes(P_Q_given_X, P_X, P_Q)
            P_XnotQ = bayes(1-P_Q_given_X, P_X, 1-P_Q)
            entropies = entropy_after_answer(P_Q, P_XQ, P_XnotQ)
            entropies[answers!=0.5]=numpy.inf
            question = entropies.argmin()
            if numpy.random.random()<epsilon:
                question = numpy.random.randint(len(items), len(questions))
            answer = raw_input(questions[question])
            counter += 1
            if answer.startswith("y") or answer.startswith("Y"):
                answers[question] = 1
                P_X = P_XQ[:, question]
                if question < len(items):
                    print "Success!"
                    return answers, question
            else:
                answers[question] = 0
                P_X = P_XnotQ[:, question]
        item_name = raw_input("I give up. X=?")
        try:
            item = items.index(item_name)
            return answers, item
        except ValueError:
            P_Q[answers!=0.5] = answers[answers!=0.5]
            add_item(P_Q, item_name)
            return answers, None
            
    while 1:
       print "Next round."
       answers, item = guess()
       if item is not None:
          update(answers, item)
