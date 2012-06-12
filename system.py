# -*- coding: utf-8 -*-
import time
import subprocess
import traceback
import fcntl
import os
import select

def run_command(command, data = None, timelimit = 8, killOnTimeout = True, log = None):
    if log:
        log.debug("Execution: %s" % (command))
    start_time = time.time()

    p = None

    try:
        p = subprocess.Popen(command,
              shell     = True,
              stdin     = subprocess.PIPE,
              stdout    = subprocess.PIPE,
              stderr    = subprocess.PIPE,
              close_fds = True)
        
        for f in (p.stdout, p.stderr):
            # get the file descriptor
            fd = f.fileno()
            # get the file's current flag settings
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            # update the file's flags to put the file into non-blocking mode.
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        
        outMessageList = []
        outMessage     = ""
        errMessageList = []
        errMessage     = ""
        
        ret = -1
        
        dataLeft = data
        
        #Wait the return code of the command
        while True:
            curTime = time.time()
            if (curTime - start_time) >= timelimit:
                if log:
                    log.warning("timeout reading stdout/stderr... Will ignore further reads.")
                if killOnTimeout:
                    if p.pid != 0 and p.pid != 1:
                        if log:
                            log.info("Killing pid %s with signal 9" % (p.pid, ))
                        os.kill(p.pid, 9)
                
                ret = 255
                
                break
            
            if p.poll() is not None:
                ret = p.returncode
            
            ## Read/Write, Prefer reading, as we fill the pipe with data from stdin..
            if p.stdin.closed:
                stdinLst = []
            else:
                stdinLst = [p.stdin, ]
            
            (rfds, wfds, efds) = select.select([p.stdout, p.stderr], stdinLst, [], 0.1)
            ## Data to read on standard output ?
            for fd, outList in ( (p.stdout, outMessageList), (p.stderr, errMessageList)):
                if fd in rfds:
                    try:
                        newRead = fd.read()
                    except IOError:
                        newRead = ""
                
                    if newRead:
                        outList.append(newRead)
            
            ## Ok, we have empty read buffers...
            if dataLeft:
                ## Try writing
                if p.stdin in wfds:
                    written = 51200
                    try:
                        p.stdin.write(dataLeft[:written].encode("utf-8"))
                    except IOError: ## Broken Pipe
                        if log:
                            log.error("Broken pipe... no more data will be written.")
                        dataLeft = None
                        continue
                    
                    dataLeft = dataLeft[(written):]
                    p.stdin.flush()
            else:
                if not p.stdin.closed:
                    p.stdin.close()
            
            if ret != -1:
                break
        
        outMessage = "".join(outMessageList)
        errMessage = "".join(errMessageList)
    
    except (OSError, IOError):
        if log:
            log.error("OSError/IOError: %s" % (traceback.format_exc()))
        if p:
            p.stdout.close()
        raise Exception("Error executing convert command.")
    
    if p:
        p.stdout.close()
        p.stderr.close()
        
    if ret == -1:
        if p and p.poll() is not None:
            ret = p.returncode
        else:
            ret = 1
    
    if log:
        log.debug("**** Exec time: %s (ret %s) ****" % (time.time() - start_time, ret))
    
    return (ret, outMessage, errMessage)

def coloriser(message, couleur):
    """
    Pour avoir une liste de couleurs, lancer dans un shell python :
    print " ".join(["\033[%im%i\033[0m" % (i,i,) for i in range(168)])

    ou regarder l'image media/images/couleurs.jpg
    """
    couleurs = {
        'noir' : 30, 'rouge' : 31, 'vert' : 32, 'jaune' : 33, 'bleu' : 34, 'violet' : 35, 'cyan' : 36, 'blanc' : 37,
        'NOIR' : 40, 'ROUGE' : 41, 'VERT' : 42, 'JAUNE' : 43, 'BLEU' : 44, 'VIOLET' : 45, 'CYAN' : 46, 'BLANC' : 47,
        'noirc' : 90,  'rougec' : 91,  'vertc' : 92,  'jaunec' : 93,  'bleuc' : 94,  'violetc' : 95,  'cyanc' : 96,  'blancc' : 97,
        'NOIRC' : 100, 'ROUGEC' : 101, 'VERTC' : 102, 'JAUNEC' : 103, 'BLEUC' : 104, 'VIOLETC' : 105, 'CYANC' : 106, 'BLANCC' : 107,
        }
    if isinstance(couleur, (str, unicode)):
        try:
            couleur = couleurs[couleur]
        except KeyError:
            couleur = 0
    return "\033[%im%s\033[0m" % (couleur, message,)

def get_term_size():
    import termios, fcntl, struct, sys

    s = struct.pack("HHHH",0,0,0,0)
    try:
        x = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
    except IOError:
        return (25,80)
    return struct.unpack("HHHH", x)[0:2]

def question_on(question, default = False):
    choix = "[o/" + coloriser("N", 'vertc') + "]"
    if default:
        choix = "[" + coloriser("O", 'vertc') + "/n]"
    print coloriser(question, 'bleuc') + " " + choix,
    reponse = raw_input()
    if not reponse:
        return default
    if reponse in ("o","O","y","Y","oui","Oui","OUI","yes","Yes","YES"):
        return True
    return False

def question_choix(question, choix, default = None):
    choix = [c.lower() for c in choix if isinstance(c, basestring)]
    reponse = None
    while reponse not in choix:
        print coloriser(question, 'bleuc') + " [" + "/". join(choix) + "] (%s) :" % (coloriser(default, 'vertc'),),
        reponse = raw_input()
        if not reponse and default:
            reponse = default
    return reponse

def centrer(texte, delta = 0):
    width = get_term_size()[1]-2
    return texte.center(width - (2 * delta))

def ligne_horizontale(char):
    width = get_term_size()[1]-2
    pat_size = len(char)
    delta = width - ((width/pat_size) * pat_size)
    return char * (width / pat_size) + char[0:delta]

def encadrer(texte, char, couleur = None):
    result = ligne_horizontale(char) + "\n"
    for ligne in texte.split("\n"):
        result += char + centrer(ligne, len(char)) + char + "\n"
    result += ligne_horizontale(char)
    if couleur:
        return coloriser(result, couleur)
    return result
    
def less(texte):
    max = get_term_size()[0]-5
    liste_lignes = texte.split("\n")
    if len(liste_lignes) >= max:
        print coloriser("Appuyer sur entrée pour passer à la suite ou appuyer sur 'q' pour arrêter", 'ROUGE')
        cpt = 0
        for line in liste_lignes:
            print line
            cpt += 1
            if cpt == max:
                cpt = 0
                rep = raw_input("")
                if rep in ("q", "Q"):
                    break
    else:
        print texte
