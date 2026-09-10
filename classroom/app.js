const welcome=document.getElementById('welcome');
const classroom=document.getElementById('classroom');
const start=document.getElementById('startLearning');
const founderPanel=document.getElementById('founderPanel');
const hearFounderButton=document.getElementById('hearFounder');
const learnerNickname=document.getElementById('learnerNickname');
const learnerClass=document.getElementById('learnerClass');
const onboardingError=document.getElementById('onboardingError');
const learnerIdentity=document.getElementById('learnerIdentity');
const showTeacherLogin=document.getElementById('showTeacherLogin');
const teacherLogin=document.getElementById('teacherLogin');
const teacherAccessKey=document.getElementById('teacherAccessKey');
const openTeacherDashboardButton=document.getElementById('openTeacherDashboard');
const teacherLoginError=document.getElementById('teacherLoginError');
const changeLearnerButton=document.getElementById('changeLearner');
const toggle=document.getElementById('toggleTeacher');
const teacherPanel=document.getElementById('teacherPanel');
const readAnswerButton=document.getElementById('readAnswer');
const handsFreeToggle=document.getElementById('handsFreeToggle');
const handsFreeHeard=document.getElementById('handsFreeHeard');
const teacherVoiceStatus=document.getElementById('teacherVoiceStatus');
const learningStatus=document.getElementById('learningStatus');
const form=document.getElementById('chatForm');
const question=document.getElementById('question');
const messages=document.getElementById('messages');
const sendButton=form.querySelector('.send');
const uploadButton=document.getElementById('uploadButton');
const cameraButton=document.getElementById('cameraButton');
const imageUpload=document.getElementById('imageUpload');
const cameraCapture=document.getElementById('cameraCapture');
const micButton=document.getElementById('micButton');
const simplifyButton=document.getElementById('simplifyButton');
const understandingButton=document.getElementById('understandingButton');
const visualButton=document.getElementById('visualButton');
const visualArea=document.getElementById('visualArea');
const visualTitle=document.getElementById('visualTitle');
const visualGraphic=document.getElementById('visualGraphic');
const visualCaption=document.getElementById('visualCaption');
const closeVisualButton=document.getElementById('closeVisual');
const mediaButton=document.getElementById('mediaButton');
const mediaArea=document.getElementById('mediaArea');
const mediaTitle=document.getElementById('mediaTitle');
const mediaFrame=document.getElementById('mediaFrame');
const mediaReplay=document.getElementById('mediaReplay');
const mediaSource=document.getElementById('mediaSource');
const closeMediaButton=document.getElementById('closeMedia');
const understandingArea=document.getElementById('understandingArea');
const understandingQuestion=document.getElementById('understandingQuestion');
const understandingForm=document.getElementById('understandingForm');
const understandingChoices=document.getElementById('understandingChoices');
const understandingFeedback=document.getElementById('understandingFeedback');
const closeUnderstandingButton=document.getElementById('closeUnderstanding');
const teachingCanvas=document.getElementById('canvas');
const canvasEmpty=document.getElementById('canvasEmpty');
const canvasWork=document.getElementById('canvasWork');
const problemPreview=document.getElementById('problemPreview');
const canvasStatus=document.getElementById('canvasStatus');
const canvasAnswer=document.getElementById('canvasAnswer');
const lessonDirector=document.getElementById('lessonDirector');
const lessonStepLabel=document.getElementById('lessonStepLabel');
const lessonStepTrack=document.getElementById('lessonStepTrack');
const previousLessonStep=document.getElementById('previousLessonStep');
const nextLessonStep=document.getElementById('nextLessonStep');
const replayLessonStep=document.getElementById('replayLessonStep');
const askLessonQuestion=document.getElementById('askLessonQuestion');
const lessonPauseNotice=document.getElementById('lessonPauseNotice');
const returnToLesson=document.getElementById('returnToLesson');
const endLesson=document.getElementById('endLesson');
const teachingStageMode=document.getElementById('teachingStageMode');
const autoTeachToggle=document.getElementById('autoTeachToggle');
const lessonChoreographyHint=document.getElementById('lessonChoreographyHint');
const teachingMemoryStatus=document.getElementById('teachingMemoryStatus');
const showStepVisual=document.getElementById('showStepVisual');
const watchStepExample=document.getElementById('watchStepExample');
const checkStepUnderstanding=document.getElementById('checkStepUnderstanding');
const canvasVoiceAvatar=document.getElementById('canvasVoiceAvatar');
const canvasVoiceAvatarStatus=canvasVoiceAvatar.querySelector('span');
const whiteboardButton=document.getElementById('whiteboardButton');
const whiteboardArea=document.getElementById('whiteboardArea');
const whiteboard=document.getElementById('whiteboard');
const penTool=document.getElementById('penTool');
const eraserTool=document.getElementById('eraserTool');
const clearBoardButton=document.getElementById('clearBoard');
const closeBoardButton=document.getElementById('closeBoard');
const submitBoardButton=document.getElementById('submitBoard');
const backToWhiteboard=document.getElementById('backToWhiteboard');
const language=document.getElementById('language');
const languageButton=document.getElementById('languageButton');
const chatButton=document.getElementById('chatButton');
const practiceButton=document.getElementById('practiceButton');
const practiceArea=document.getElementById('practiceArea');
const practiceSetup=document.getElementById('practiceSetup');
const practiceQuestion=document.getElementById('practiceQuestion');
const practiceClass=document.getElementById('practiceClass');
const practiceTerm=document.getElementById('practiceTerm');
const practiceClassSummary=document.getElementById('practiceClassSummary');
const practiceTopic=document.getElementById('practiceTopic');
const practiceDifficulty=document.getElementById('practiceDifficulty');
const practiceCount=document.getElementById('practiceCount');
const startPracticeButton=document.getElementById('startPractice');
const startDiagnosticButton=document.getElementById('startDiagnostic');
const practiceProgress=document.getElementById('practiceProgress');
const practiceScore=document.getElementById('practiceScore');
const practiceContext=document.getElementById('practiceContext');
const practicePrompt=document.getElementById('practicePrompt');
const practiceForm=document.getElementById('practiceForm');
const practiceAnswer=document.getElementById('practiceAnswer');
const showHintButton=document.getElementById('showHint');
const nextPracticeButton=document.getElementById('nextPractice');
const closePracticeButton=document.getElementById('closePractice');
const practiceFeedback=document.getElementById('practiceFeedback');
const practiceResults=document.getElementById('practiceResults');
const resultPercentage=document.getElementById('resultPercentage');
const resultScore=document.getElementById('resultScore');
const resultRecommendation=document.getElementById('resultRecommendation');
const missedReview=document.getElementById('missedReview');
const practiceAgainButton=document.getElementById('practiceAgain');
const changePracticeTopicButton=document.getElementById('changePracticeTopic');
const exitPracticeResultsButton=document.getElementById('exitPracticeResults');
const viewProgressFromResults=document.getElementById('viewProgressFromResults');
const progressButton=document.getElementById('progressButton');
const progressArea=document.getElementById('progressArea');
const progressLoading=document.getElementById('progressLoading');
const progressEmpty=document.getElementById('progressEmpty');
const progressDashboard=document.getElementById('progressDashboard');
const closeProgressButton=document.getElementById('closeProgress');
const emptyStartPractice=document.getElementById('emptyStartPractice');
const progressSessions=document.getElementById('progressSessions');
const progressQuestions=document.getElementById('progressQuestions');
const progressAverage=document.getElementById('progressAverage');
const progressStrongest=document.getElementById('progressStrongest');
const progressRecommendation=document.getElementById('progressRecommendation');
const weeklySessions=document.getElementById('weeklySessions');
const weeklyQuestions=document.getElementById('weeklyQuestions');
const weeklyScore=document.getElementById('weeklyScore');
const weeklyImprovement=document.getElementById('weeklyImprovement');
const weeklyStrongest=document.getElementById('weeklyStrongest');
const weeklyFocus=document.getElementById('weeklyFocus');
const weeklyNextAction=document.getElementById('weeklyNextAction');
const practiceRecommendation=document.getElementById('practiceRecommendation');
const learningPath=document.getElementById('learningPath');
const progressTopics=document.getElementById('progressTopics');
const recentSessions=document.getElementById('recentSessions');
const progressStorageNotice=document.getElementById('progressStorageNotice');
const teacherDashboardButton=document.getElementById('teacherDashboardButton');
const teacherDashboard=document.getElementById('teacherDashboard');
const teacherDashboardContent=document.getElementById('teacherDashboardContent');
const closeTeacherDashboard=document.getElementById('closeTeacherDashboard');
const teacherClass=document.getElementById('teacherClass');
const downloadTeacherReport=document.getElementById('downloadTeacherReport');
const openQaChecklist=document.getElementById('openQaChecklist');
const qaChecklist=document.getElementById('qaChecklist');
const qaChecklistItems=document.getElementById('qaChecklistItems');
const qaCompleted=document.getElementById('qaCompleted');
const qaPassed=document.getElementById('qaPassed');
const qaBlockers=document.getElementById('qaBlockers');
const qaReleaseStatus=document.getElementById('qaReleaseStatus');
const downloadQaReport=document.getElementById('downloadQaReport');
const closeQaChecklist=document.getElementById('closeQaChecklist');
let currentPractice=null;
let currentPracticeSummary=null;
let practiceMode='practice';
let currentProgress=null;
let sessionToken=null;
let previewUrl=null;
let mediaRecorder=null;
let micStream=null;
let recordedChunks=[];
let teacherSpeechController=null;
let teacherSpeechRequest=0;
let teacherAudioContext=null;
let teacherAudioAnalyser=null;
const teacherAudioSources=new Set();
const founderAudioSources=new Set();
let teacherStreamComplete=false;
let founderStreamComplete=false;
let teacherSpeechPaused=false;
let founderSpeechController=null;
let founderSpeechRequest=0;
let avatarMotionFrame=null;
let activeAvatarRig=null;
let avatarEnergy=0;
let showVoiceAnswerAvatar=false;
let currentLesson=null;
const lessonHistory=[];
let lessonInterruption=null;
const teachingStage={mode:'lesson',bookmark:0};
const lessonChoreography={enabled:true,visited:new Set(),timer:null};
let learnerMemoryId='';
let adaptiveMemory={replays:0,simplifications:0,questions:0,correct:0,incorrect:0};
const handsFree={enabled:false,recognition:null,processing:false,restartTimer:null,phraseTimer:null,phraseBuffer:'',bufferConfidence:0,pending:'',lastPhrase:'',lastAt:0,armedUntil:0,bargeInAt:0,ignorePauseUntil:0};
let languageSwitchRequest=0;
let teacherAudioKeepAlive=null;
let understandingCheckId=null;
let mediaReplayTimer=null;
let drawing=false;
let drawingTool='pen';
let boardHasInk=false;
let teacherDashboardAccessKey='';
let currentTeacherDashboard=null;
const boardContext=whiteboard.getContext('2d');
const qaChecks={
  'Learner journey':['Fresh onboarding opens','Class selection controls curriculum','Returning nickname restores progress','Change learner clears the visible session'],
  'Diagnostic assessment':['JSS1 term diagnostic completes','JSS2 term diagnostic completes','JSS3 term diagnostic completes','Topic scores and recommendation are correct','Diagnostic result restores after a new session'],
  'Practice and personalisation':['Questions do not repeat or freeze','Correct and incorrect feedback explains the answer','Auto difficulty moves up after two strong sessions','Auto difficulty moves down after two low sessions','Continue Learning opens the recommended topic'],
  'Language and voice':['English voice input and reply work','Yorùbá input, numbers and reply work','Igbo input and reply work','Hausa input and reply work','Language switches during Practice','Audio pauses and continues from the same place','Voice questions receive automatic spoken answers'],
  'Progress and Teacher View':['Practice result saves to Google Sheets','Diagnostic saves to its separate worksheet','Weekly learner summary is correct','Teacher class selector and trends are correct','Diagnostic class aggregates contain no identities','Practice and QA CSV reports download'],
  'Devices':['Android Chrome works','Desktop Chrome or Edge works','iPhone or Safari checked when available','No clipped controls or horizontal scrolling']
};
const savedLanguage=localStorage.getItem('roboTeacherLanguage');
if(['English','Yoruba','Igbo','Hausa'].includes(savedLanguage))language.value=savedLanguage;
const dashboardCopy={
  English:{sessions:'Sessions',questions:'Questions',overall:'Overall score',strongest:'Strongest topic',next:'Recommended next step',continue:'Continue Learning →',week:'This week',weekStrongest:'Strongest this week',attention:'Needs attention',learners:'Learners',average:'Average',weakest:'Weakest topic',score:'Score',trend:'Trend',noData:'Not enough data',noCompare:'No previous-week comparison',noChange:'No score change',sixWeek:'Six-week performance trend',topicPerformance:'Topic performance'},
  Yoruba:{sessions:'Ìgbà ìdánwò',questions:'Àwọn ìbéèrè',overall:'Àpapọ̀ máàkì',strongest:'Kókó tó dára jù',next:'Ohun tó yẹ kó tẹ̀lé',continue:'Tẹ̀síwájú Kíkọ́ →',week:'Ọ̀sẹ̀ yìí',weekStrongest:'Kókó tó dára jù lọ ọ̀sẹ̀ yìí',attention:'Ohun tó nílò àtúnṣe',learners:'Àwọn akẹ́kọ̀ọ́',average:'Àpapọ̀',weakest:'Kókó tó nílò iṣẹ́ síi',score:'Máàkì',trend:'Bí máàkì ṣe ń lọ',noData:'Kò tíì sí data tó',noCompare:'Kò tíì sí ọ̀sẹ̀ míì láti fi wé e',noChange:'Máàkì kò yí padà',sixWeek:'Bí máàkì ṣe lọ fún ọ̀sẹ̀ mẹ́fà',topicPerformance:'Máàkì àwọn kókó'},
  Igbo:{sessions:'Oge omume',questions:'Ajụjụ',overall:'Akara niile',strongest:'Isiokwu kacha mma',next:'Ihe ị ga-eme ọzọ',continue:'Gaa n’Ihu n’Ịmụ →',week:'Izu a',weekStrongest:'Isiokwu kacha mma n’izu a',attention:'Ihe chọrọ mgbakwunye',learners:'Ụmụ akwụkwọ',average:'Nkezi',weakest:'Isiokwu chọrọ ọrụ ọzọ',score:'Akara',trend:'Mgbanwe akara',noData:'Data ezughị',noCompare:'Enweghị izu gara aga iji tụnyere',noChange:'Akara agbanwebeghị',sixWeek:'Mgbanwe akara izu isii',topicPerformance:'Nsonaazụ isiokwu'},
  Hausa:{sessions:'Zaman atisaye',questions:'Tambayoyi',overall:'Jimillar maki',strongest:'Darasi mafi ƙarfi',next:'Mataki na gaba',continue:'Ci Gaba da Koyo →',week:'Wannan makon',weekStrongest:'Darasi mafi ƙarfi a makon nan',attention:'Abin da ke buƙatar kulawa',learners:'Dalibai',average:'Matsakaici',weakest:'Darasi mai buƙatar ƙarin aiki',score:'Maki',trend:'Canjin maki',noData:'Babu isasshen bayani',noCompare:'Babu makon baya don kwatantawa',noChange:'Maki bai canza ba',sixWeek:'Canjin maki na makonni shida',topicPerformance:'Sakamakon darussa'}
};
const resultCopy={
  English:{score:(correct,total)=>`${correct} out of ${total} correct`,diagnostic:'Diagnostic topic results',review:'Questions to review',perfect:'Perfect score!',perfectNote:'You answered every question correctly. Excellent work!',yourAnswer:'Your answer',noAnswer:'No answer',correctAnswer:'Correct answer',again:'Practise Again',progress:'View Progress',change:'Change Topic',recommended:'Practise Recommended Topic',exit:'Exit Practice'},
  Yoruba:{score:(correct,total)=>`${correct} nínú ${total} ló dáa`,diagnostic:'Àbájáde kókó nínú ìdánwò',review:'Àwọn ìbéèrè láti tún wo',perfect:'Gbogbo rẹ̀ dáa!',perfectNote:'O dáhùn gbogbo ìbéèrè dáadáa. Iṣẹ́ rere!',yourAnswer:'Ìdáhùn rẹ',noAnswer:'Kò sí ìdáhùn',correctAnswer:'Ìdáhùn tó tọ́',again:'Ṣe lẹ́ẹ̀kan sí',progress:'Wo Ìtẹ̀síwájú',change:'Yí Kókó Padà',recommended:'Ṣe Kókó Tí A Dábàá',exit:'Jáde nínú Practice'},
  Igbo:{score:(correct,total)=>`${correct} n’ime ${total} ziri ezi`,diagnostic:'Nsona isiokwu ule',review:'Ajụjụ ị ga-elegharị anya',perfect:'Akara zuru oke!',perfectNote:'Ị zara ajụjụ niile nke ọma. Ezigbo ọrụ!',yourAnswer:'Azịza gị',noAnswer:'Enweghị azịza',correctAnswer:'Azịza ziri ezi',again:'Mee ọzọ',progress:'Lee Ọganihu',change:'Gbanwee Isiokwu',recommended:'Mee Isiokwu A Tụrụ Aro',exit:'Kwidata Practice'},
  Hausa:{score:(correct,total)=>`${correct} cikin ${total} daidai`,diagnostic:'Sakamakon batutuwan gwaji',review:'Tambayoyin da za a sake dubawa',perfect:'Cikakken maki!',perfectNote:'Ka amsa duk tambayoyin daidai. Madalla!',yourAnswer:'Amsarka',noAnswer:'Babu amsa',correctAnswer:'Amsa daidai',again:'Sake Gwaji',progress:'Duba Ci Gaba',change:'Canja Batu',recommended:'Gwada Batun da Aka Ba da Shawara',exit:'Fita daga Practice'}
};
function dcopy(key){return (dashboardCopy[language.value]||dashboardCopy.English)[key]}
const pathCopy={English:{not_started:'Not started',needs_practice:'Needs practice',mastered:'Mastered',recommended:'Recommended next',continue:'Continue →',start:'Start',practise:'Practise'},Yoruba:{not_started:'Kò tíì bẹ̀rẹ̀',needs_practice:'Ó nílò Practice',mastered:'Ó ti mọ̀ ọ́',recommended:'Èyí ló kàn',continue:'Tẹ̀síwájú →',start:'Bẹ̀rẹ̀',practise:'Ṣe Practice'},Igbo:{not_started:'Amalitebeghị',needs_practice:'Ọ chọrọ Practice',mastered:'Ọ mụtala ya',recommended:'Ihe na-esote',continue:'Gaa n’ihu →',start:'Bido',practise:'Mee Practice'},Hausa:{not_started:'Ba a fara ba',needs_practice:'Yana buƙatar Practice',mastered:'An iya shi',recommended:'Mataki na gaba',continue:'Ci gaba →',start:'Fara',practise:'Yi Practice'}};
const diagnosticLabels={English:{title:'Diagnostic placement',completed:'Completed tests',learners:'Learners assessed',average:'Average score',focus:'Most common starting topic'},Yoruba:{title:'Ìdánwò ìbẹ̀rẹ̀',completed:'Ìdánwò tó parí',learners:'Akẹ́kọ̀ọ́ tí a yẹ̀wò',average:'Àpapọ̀ máàkì',focus:'Kókó ìbẹ̀rẹ̀ tó wọ́pọ̀'},Igbo:{title:'Nnwale mbido',completed:'Nnwale emechara',learners:'Ụmụ akwụkwọ enyochara',average:'Nkezi akara',focus:'Isiokwu mmalite kacha pụta'},Hausa:{title:'Gwajin farawa',completed:'Gwajin da aka kammala',learners:'Daliban da aka gwada',average:'Matsakaicin maki',focus:'Darasin farawa mafi yawa'}};
function learnerRecommendation(data){
  if(language.value==='English')return data.recommendation;const topic=data.recommended_topic,term=data.recommended_term,level=data.recommended_difficulty;
  if(language.value==='Yoruba')return data.recommendation_reason==='strengthen'?`Tun ${topic} ṣe ní ipele ${level}. Wo gbogbo àlàyé dáadáa.`:`Tẹ̀síwájú pẹ̀lú ${topic} ní ipele ${level}.`;
  if(language.value==='Igbo')return data.recommendation_reason==='strengthen'?`Megharịa ${topic} n’ọkwa ${level}, gụọkwa nkọwa niile.`:`Gaa n’ihu na ${topic} n’ọkwa ${level}.`;
  return data.recommendation_reason==='strengthen'?`Sake yin ${topic} a matakin ${level}, ka duba duk bayanin.`:`Ci gaba da ${topic} a matakin ${level}.`;
}
function weeklyAction(week){
  if(language.value==='English')return week.next_action;const topic=week.focus_topic||'';
  if(language.value==='Yoruba')return !week.sessions?'Ṣe Practice kan kí o lè rí ìmọ̀ràn ọ̀sẹ̀.':week.percentage<50?`Wo àpẹẹrẹ ${topic}, kí o sì ṣe ipele tó rọrùn.`:week.percentage<80?`Tun ${topic} ṣe, kí o sì wo ibi tí o ṣìṣe.`:`O ṣe dáadáa. Gbìyànjú ipele tó kàn ní ${topic}.`;
  if(language.value==='Igbo')return !week.sessions?'Mee otu Practice ka ị nweta ndụmọdụ izu.':week.percentage<50?`Gụọ ihe atụ ${topic}, wee mee ọkwa dị mfe.`:week.percentage<80?`Megharịa ${topic} ma lelee ebe i mejọrọ.`:`Ị mere nke ọma. Gbalịa ọkwa ọzọ na ${topic}.`;
  return !week.sessions?'Yi Practice ɗaya domin samun shawarar mako.':week.percentage<50?`Duba misalan ${topic}, sannan ka yi mataki mai sauƙi.`:week.percentage<80?`Sake yin ${topic}, ka duba kurakuranka.`:`Ka yi kyau. Gwada mataki na gaba a ${topic}.`;
}
function teacherAction(data){
  if(language.value==='English')return data.weekly_summary.action;const week=data.weekly_summary,topic=week.weakest_topic||'';
  if(language.value==='Yoruba')return !week.sessions?'Kò sí Practice lọ́sẹ̀ yìí. Yan ìdánwò tó bá kíláàsì mu.':week.percentage<50?`Tun ${topic} kọ́ pẹ̀lú àpẹẹrẹ, kí o sì fún wọn ní Easy.`:week.percentage<80?`Ṣe àtúnyẹ̀wò ${topic} pẹ̀lú ẹgbẹ́ kékeré, kí wọn tún Practice ṣe.`:`Kíláàsì ṣe dáadáa. Fún wọn ní Challenge lórí ${topic}.`;
  if(language.value==='Igbo')return !week.sessions?'Enweghị Practice n’izu a. Nye otu omume dabara na klas.':week.percentage<50?`Kụzie ${topic} ọzọ site n’ihe atụ, nyezie Easy.`:week.percentage<80?`Legharịa ${topic} na obere otu, nyezie Practice ọzọ.`:`Klas mere nke ọma. Nye Challenge na ${topic}.`;
  return !week.sessions?'Babu Practice a makon nan. Ba ajin atisayen da ya dace.':week.percentage<50?`Sake koyar da ${topic} da misalai, sannan a yi Easy.`:week.percentage<80?`Sake duba ${topic} a ƙaramin rukuni, sannan a sake Practice.`:`Ajin ya yi kyau. Ba su Challenge a ${topic}.`;
}
function teacherOverallAction(data){
  if(language.value==='English')return data.recommendation;const weakest=data.topics[0],topic=data.weakest_topic||'';
  if(language.value==='Yoruba')return !data.questions?'Jẹ́ kí àwọn akẹ́kọ̀ọ́ ṣe Practice kan kí o tó ṣètò ìrànlọ́wọ́.':weakest.percentage<50?`Tun ${topic} kọ́ pẹ̀lú àpẹẹrẹ, kí o sì fún wọn ní Easy.`:weakest.percentage<80?`Ṣe àtúnyẹ̀wò ${topic}, kí wọn sì tún Practice ṣe.`:`Kíláàsì ṣe dáadáa. Lo Challenge fún ${topic}.`;
  if(language.value==='Igbo')return !data.questions?'Gwa ụmụ akwụkwọ ka ha mee otu Practice tupu ịhazi enyemaka.':weakest.percentage<50?`Kụzie ${topic} ọzọ site n’ihe atụ, nyezie Easy.`:weakest.percentage<80?`Legharịa ${topic}, nyezie Practice ọzọ.`:`Klas mere nke ọma. Jiri Challenge maka ${topic}.`;
  return !data.questions?'Ka dalibai yi Practice ɗaya kafin a shirya taimako.':weakest.percentage<50?`Sake koyar da ${topic} da misalai, sannan a yi Easy.`:weakest.percentage<80?`Sake duba ${topic}, sannan a sake Practice.`:`Ajin ya yi kyau. Yi amfani da Challenge a ${topic}.`;
}
function weeklyImprovementText(week){
  if(language.value==='English')return week.improvement_points===null?'Complete another week to measure improvement.':week.improvement_points>0?`Improved by ${week.improvement_points} percentage points.`:week.improvement_points<0?`Down ${Math.abs(week.improvement_points)} points—review the recommended topic.`:'Your score is steady compared with last week.';
  const points=Math.abs(week.improvement_points||0);
  if(language.value==='Yoruba')return week.improvement_points===null?'Parí ọ̀sẹ̀ míì ká lè rí ìlọsíwájú.':week.improvement_points>0?`Máàkì pọ̀ sí i pẹ̀lú ${points}.`:week.improvement_points<0?`Máàkì dín kù pẹ̀lú ${points}; tún kókó náà ṣe.`:'Máàkì dúró bí ọ̀sẹ̀ tó kọjá.';
  if(language.value==='Igbo')return week.improvement_points===null?'Mechaa izu ọzọ ka a tụọ ọganihu.':week.improvement_points>0?`Akara rịrị site na ${points}.`:week.improvement_points<0?`Akara dara site na ${points}; megharịa isiokwu ahụ.`:'Akara gị ka dị ka izu gara aga.';
  return week.improvement_points===null?'Kammala wani mako domin a auna ci gaba.':week.improvement_points>0?`Maki ya ƙaru da ${points}.`:week.improvement_points<0?`Maki ya ragu da ${points}; sake duba darasin.`:'Maki bai canza daga makon baya ba.';
}
// Always show clean onboarding. Anonymous progress profiles remain on-device
// and reconnect when the same nickname and class are entered again.
learnerNickname.value='';
learnerClass.value='JSS2';
const practiceCurriculum={
  JSS1:{
    'First Term':['Whole Numbers','Factors, Multiples, LCM & HCF','Fractions','Estimation'],
    'Second Term':['Decimals & Approximation','Number Bases (Binary)','Positive & Negative Integers','Introductory Algebra'],
    'Third Term':['Simple Equations','Plane Shapes & Mensuration','3D Shapes & Volume','Angles & Construction','Data Presentation','Mean, Median & Mode']
  },
  JSS2:{
    'First Term':['Standard Form','Prime Factors, Squares & Roots','Fractions, Ratios, Decimals & Percentages','Commercial Arithmetic','Approximation','Directed Numbers','Algebraic Expressions & Factorisation','Algebraic Fractions'],
    'Second Term':['Simple Equations','Linear Inequalities','Linear Graphs','Plane Shapes & Scale Drawing'],
    'Third Term':['Angles & Polygons','Elevation & Depression','Bearings & Distances','Pythagoras & Mensuration','Statistics & Data Presentation','Probability']
  },
  JSS3:{
    'First Term':['Number Bases','Rational & Irrational Numbers','Ratio, Proportion & Variation','Approximation','Factorisation & Quadratic Expressions','Formulae & Change of Subject'],
    'Second Term':['Equations Involving Fractions','Simultaneous Equations','Similar Shapes','Trigonometry','Geometry & Construction'],
    'Third Term':['Mensuration & Volumes','Statistics & Averages','Pie Charts','Commercial Arithmetic']
  }
};
const classTopics=Object.fromEntries(Object.entries(practiceCurriculum).map(([level,terms])=>[level,Object.values(terms).flat()]));
function updatePracticeTopics(){
  const selectedClass=practiceClass.value;const selectedTerm=practiceTerm.value;const previous=practiceTopic.value;const topics=practiceCurriculum[selectedClass][selectedTerm];practiceTopic.replaceChildren(...topics.map(topic=>{const option=document.createElement('option');option.textContent=topic;return option}));
  if(topics.includes(previous))practiceTopic.value=previous;
  practiceClassSummary.textContent=`Showing ${selectedClass} Mathematics · ${selectedTerm} (${topics.length} topics)`;
}
practiceClass.value=learnerClass.value;updatePracticeTopics();
learnerClass.addEventListener('change',()=>{practiceClass.value=learnerClass.value;practiceTerm.value='First Term';updatePracticeTopics()});practiceClass.addEventListener('change',()=>{practiceTerm.value='First Term';updatePracticeTopics()});practiceTerm.addEventListener('change',updatePracticeTopics);

function loadAdaptiveMemory(profileId){
  learnerMemoryId=profileId;
  try{adaptiveMemory={replays:0,simplifications:0,questions:0,correct:0,incorrect:0,...JSON.parse(localStorage.getItem(`roboTeacherMemory:${profileId}`)||'{}')}}catch(_error){adaptiveMemory={replays:0,simplifications:0,questions:0,correct:0,incorrect:0}}
  renderAdaptiveMemory();
}

function recordLearningSignal(signal){
  if(!learnerMemoryId||!(signal in adaptiveMemory))return;
  adaptiveMemory[signal]=Math.min(999,(Number(adaptiveMemory[signal])||0)+1);
  localStorage.setItem(`roboTeacherMemory:${learnerMemoryId}`,JSON.stringify(adaptiveMemory));
  renderAdaptiveMemory();
}

function adaptiveSupportLevel(){
  const difficulty=adaptiveMemory.replays+adaptiveMemory.simplifications*2+adaptiveMemory.questions+adaptiveMemory.incorrect*2;
  const confidence=adaptiveMemory.correct*2;
  if(difficulty>=confidence+4)return 'support';
  if(confidence>=difficulty+4)return 'challenge';
  return 'learning';
}

function renderAdaptiveMemory(){
  if(!teachingMemoryStatus)return;
  const level=adaptiveSupportLevel();
  teachingMemoryStatus.dataset.level=level;
  teachingMemoryStatus.textContent=level==='support'?'Extra support active':level==='challenge'?'Ready for challenge':'Learning your pace';
}

function adaptivePromptContext(){
  const level=adaptiveSupportLevel();
  if(level==='support')return 'Teaching memory: this learner benefits from shorter steps, one familiar example, and a brief check after the explanation.';
  if(level==='challenge')return 'Teaching memory: this learner is answering confidently. Keep the explanation concise and include one slightly more challenging follow-up.';
  return 'Teaching memory: use clear age-appropriate steps and one short understanding check.';
}

function handsFreeLanguage(){return {English:'en-NG',Yoruba:'yo-NG',Igbo:'ig-NG',Hausa:'ha-NG'}[language.value]||'en-NG'}

function updateHandsFreeStatus(message){
  handsFreeToggle.textContent=handsFree.enabled?(message||'Listening…'):'Wake-word';
  handsFreeToggle.setAttribute('aria-pressed',String(handsFree.enabled));
  handsFreeToggle.setAttribute('aria-label',handsFree.enabled?'Disable hands-free teaching':'Enable hands-free teaching');
}

function showHandsFreeHeard(message){handsFreeHeard.textContent=message;handsFreeHeard.classList.toggle('hidden',!message)}

function speechAlternativeScore(alternative){
  const transcript=(alternative?.transcript||'').trim().toLowerCase();
  if(!transcript)return -Infinity;
  const confidence=Number(alternative.confidence)||0;
  const wordCount=transcript.split(/\s+/).length;
  let score=confidence*8+Math.min(wordCount,18)*.12;
  if(/\b(?:robo|robot|robotic)\s*(?:teacher|tutor|feature)\b/.test(transcript))score+=4;
  if(/\b(?:square root|square route|squared root|fraction|multiply|divide|division|equation|angle|graph|plus|minus|solve|calculate)\b/.test(transcript))score+=3;
  if(/\b(?:pause|pulse|paws|pose|pores|continue|resume|repeat|visual|diagram)\b/.test(transcript))score+=2;
  return score;
}

function chooseBestSpeechAlternative(result){
  let best=result[0],bestScore=speechAlternativeScore(best);
  for(let index=1;index<result.length;index++){
    const score=speechAlternativeScore(result[index]);
    if(score>bestScore){best=result[index];bestScore=score}
  }
  return best;
}

function normalizeSpokenIntent(phrase){
  return phrase.toLowerCase().replace(/\b(?:square route|squared root)\b/g,'square root').replace(/^(?:pulse|pals|paws|pose|pores)$/,'pause').replace(/^(?:continues|continue you)$/,'continue').trim();
}

function clearHandsFreePhraseBuffer(){
  clearTimeout(handsFree.phraseTimer);handsFree.phraseTimer=null;handsFree.phraseBuffer='';handsFree.bufferConfidence=0;
}

function openHandsFreeFollowUpWindow(){
  handsFree.armedUntil=Date.now()+15000;updateHandsFreeStatus('Ask or say Continue…');setLearningStatus('Teacher paused — ask a follow-up or say Continue','paused');
}

function handsFreeBargeIn(result){
  const alternatives=Array.from(result).map(item=>(item.transcript||'').trim()).filter(Boolean);
  const command=alternatives.find(transcript=>/^(?:(?:hey\s+)?(?:robo|robot|robotic)\s*(?:teacher|tutor|feature)[\s,.:;-]*)?(?:please\s+)?(?:pause|pulse|pals|paws|pose|pores)$/i.test(transcript));
  if(command&&Date.now()<handsFree.ignorePauseUntil)return true;
  if(!teacherPanel.classList.contains('speaking')||Date.now()-handsFree.bargeInAt<1200)return false;
  const wake=alternatives.find(transcript=>/(?:^|\s)(?:hey\s+)?(?:robo|robot|robotic)\s*(?:teacher|tutor|feature)\b/i.test(transcript));
  if(!command&&!wake)return false;
  handsFree.bargeInAt=Date.now();clearHandsFreePhraseBuffer();void pauseTeacherAudio();handsFree.armedUntil=Date.now()+7000;
  if(command){
    const interpreted=normalizeSpokenIntent(command.toLowerCase().replace(/^(?:(?:hey\s+)?(?:robo|robot|robotic)\s*(?:teacher|tutor|feature)[\s,.:;-]*)?(?:please\s+)?/i,''));
    handsFree.pending='';handsFree.ignorePauseUntil=Date.now()+1800;openHandsFreeFollowUpWindow();showHandsFreeHeard(`Heard: “${command}” · Teacher paused. Ask your follow-up within 15 seconds, or say “Continue”.`);return true;
  }
  showHandsFreeHeard(`Heard: “${wake}” — teacher paused so I can hear you.`);updateHandsFreeStatus('Ask your question…');return false;
}

function queueHandsFreePhrase(rawPhrase,confidence=0){
  const phrase=rawPhrase.trim();if(!phrase)return;
  clearTimeout(handsFree.phraseTimer);
  handsFree.phraseBuffer=[handsFree.phraseBuffer,phrase].filter(Boolean).join(' ').trim();
  handsFree.bufferConfidence=Math.max(handsFree.bufferConfidence,Number(confidence)||0);
  handsFree.phraseTimer=setTimeout(()=>{
    const buffered=handsFree.phraseBuffer,bufferedConfidence=handsFree.bufferConfidence;clearHandsFreePhraseBuffer();handleHandsFreePhrase(buffered,bufferedConfidence);
  },800);
}

function startHandsFreeListening(){
  if(!handsFree.enabled||handsFree.processing||!handsFree.recognition)return;
  clearTimeout(handsFree.restartTimer);handsFree.recognition.lang=handsFreeLanguage();
  try{handsFree.recognition.start();updateHandsFreeStatus(lessonInterruption?'Ask your question…':'Listening…')}catch(_error){/* Recognition is already active. */}
}

function stopHandsFreeListening(){clearTimeout(handsFree.restartTimer);try{handsFree.recognition?.stop()}catch(_error){/* Already stopped. */}}

function resumeBookmarkedLessonByVoice(){
  stopTeacherAudio();lessonInterruption=null;lessonDirector.classList.remove('lesson-paused');
  if(lessonHistory.length){
    const lesson=lessonHistory.pop();startLessonDirector(lesson.text,lesson.index);canvasStatus.textContent='Previous lesson resumed';setLearningStatus(`Returned to lesson step ${lesson.index+1}`);
  }else if(currentLesson)renderCurrentLessonStep();
  const step=currentLesson?.steps[currentLesson.index];
  if(step)void speakText(step,true,true);else void resumeTeacherAudio();
}

function continueHandsFreeTeaching(){
  if(lessonHistory.length||lessonInterruption){resumeBookmarkedLessonByVoice();return}
  if(teacherSpeechPaused){void resumeTeacherAudio();return}
  if(currentLesson){renderCurrentLessonStep();const step=currentLesson.steps[currentLesson.index];if(step)void speakText(step,true,true)}
}

function executeHandsFreeIntent(phrase){
  const command=phrase.toLowerCase().replace(/[^a-zà-ž0-9\s()+,.?=\-]/gu,'').trim();
  const pauseCommand=/^(pause|stop|dúró|kwụsị|dakatar)$/.test(command);
  const continueCommand=/^(continue|resume|go on|tẹ̀síwájú|gaa nihu|ci gaba)$/.test(command);
  const replayCommand=/^(explain (that )?again|repeat( that)?|say (that )?again)$/.test(command);
  const visualCommand=/^(show (me )?(a )?visual|show (the )?diagram)$/.test(command);
  const stopListeningCommand=/^(stop listening|turn off|goodbye)$/.test(command);
  if(teacherPanel.classList.contains('speaking')&&!pauseCommand&&!continueCommand&&!replayCommand&&!visualCommand&&!stopListeningCommand)return;
  if(pauseCommand){
    if(teacherPanel.classList.contains('speaking'))void pauseTeacherAudio();else if(currentLesson)pauseLessonForQuestion('voice');
    openHandsFreeFollowUpWindow();return;
  }
  if(continueCommand){
    continueHandsFreeTeaching();
    updateHandsFreeStatus('Listening…');return;
  }
  if(replayCommand){if(currentLesson){recordLearningSignal('replays');void speakText(currentLesson.steps[currentLesson.index],true,true)}updateHandsFreeStatus('Listening…');return}
  if(visualCommand){void showVisualExplanation();updateHandsFreeStatus('Listening…');return}
  if(stopListeningCommand){
    handsFree.enabled=false;handsFree.processing=false;stopHandsFreeListening();updateHandsFreeStatus();showHandsFreeHeard('Wake-word listening is off.');setLearningStatus('Wake-word teaching off');return;
  }
  if(currentLesson&&!lessonInterruption)pauseLessonForQuestion('voice');
  handsFree.processing=true;stopHandsFreeListening();question.value=phrase;form.requestSubmit();
}

function handleHandsFreePhrase(rawPhrase,confidence=0){
  const phrase=rawPhrase.trim();if(!phrase)return;
  const now=Date.now();if(phrase===handsFree.lastPhrase&&now-handsFree.lastAt<1800)return;handsFree.lastPhrase=phrase;handsFree.lastAt=now;
  const normalized=phrase.toLowerCase().replace(/[^a-zà-ž0-9\s()+,.?=\-]/gu,'').trim();
  const wake=normalized.match(/^(?:hey\s+)?(?:robo|robot|robotic)\s*(?:teacher|tutor|feature)\b[\s,.:;-]*(.*)$/);
  const pausedControl=teacherSpeechPaused&&/^(?:continue|continues|continue you|resume|go on|tẹ̀síwájú|gaa nihu|ci gaba)$/.test(normalized);
  const clarificationReply=Boolean(handsFree.pending);
  let intent='';
  if(wake){
    intent=wake[1].trim().replace(/[,.?!:;]+$/,'').trim();handsFree.armedUntil=now+7000;
  }else if(pausedControl){
    intent=normalized;
  }else if(clarificationReply){
    intent=normalized.replace(/[,.?!:;]+$/,'').trim();
  }else if(now<handsFree.armedUntil){
    intent=normalized.replace(/[,.?!:;]+$/,'').trim();
  }else{showHandsFreeHeard(`Heard: “${phrase}” — start with “Robo-Teacher”.`);return}
  showHandsFreeHeard(`Heard: “${phrase}”`);
  const interpretedIntent=normalizeSpokenIntent(intent);
  if(interpretedIntent!==intent)showHandsFreeHeard(`Heard: “${phrase}” · Interpreted: “${interpretedIntent}”`);
  intent=interpretedIntent;
  if(/^(confirm|yes|yes please|correct)$/.test(intent)&&handsFree.pending){const pending=handsFree.pending;handsFree.pending='';handsFree.armedUntil=0;showHandsFreeHeard(`Confirmed: “${pending}”`);executeHandsFreeIntent(pending);return}
  if(/^(no|nope|cancel|try again|listen again)$/.test(intent)&&handsFree.pending){handsFree.pending='';handsFree.armedUntil=0;updateHandsFreeStatus('Listening…');showHandsFreeHeard('Okay—please say “Robo-Teacher” and try again.');return}
  if(handsFree.pending&&intent!==handsFree.pending){handsFree.pending='';showHandsFreeHeard(`Correction heard: “${intent}”`)}
  if(!intent){updateHandsFreeStatus('Command ready…');showHandsFreeHeard('Wake word heard. Say the command within 7 seconds.');return}
  if(confidence>0&&confidence<.55){handsFree.pending=intent;handsFree.armedUntil=now+15000;updateHandsFreeStatus('Please confirm…');showHandsFreeHeard(`Did you mean “${intent}”? Say “Yes”, “No”, “Try again”, or say the correction.`);return}
  handsFree.pending='';handsFree.armedUntil=0;executeHandsFreeIntent(intent);
}

function enableHandsFree(){
  const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!Recognition){addMessage('Hands-free commands are not supported in this browser. You can still use the Voice button.','teacher');return;}
  handsFree.recognition=new Recognition();handsFree.recognition.continuous=true;handsFree.recognition.interimResults=true;handsFree.recognition.maxAlternatives=5;
  handsFree.recognition.addEventListener('result',event=>{for(let index=event.resultIndex;index<event.results.length;index++){const result=event.results[index];if(handsFreeBargeIn(result))continue;const alternative=chooseBestSpeechAlternative(result),transcript=(alternative?.transcript||'').trim();if(!transcript)continue;if(result.isFinal)queueHandsFreePhrase(transcript,alternative.confidence);else showHandsFreeHeard(`Hearing: “${transcript}…”`)}});
  handsFree.recognition.addEventListener('end',()=>{if(handsFree.enabled&&!handsFree.processing)handsFree.restartTimer=setTimeout(startHandsFreeListening,350)});
  handsFree.recognition.addEventListener('error',event=>{if(event.error==='not-allowed'){handsFree.enabled=false;updateHandsFreeStatus();addMessage('Microphone permission is needed for hands-free teaching.','teacher')}});
  handsFree.enabled=true;handsFree.pending='';handsFree.armedUntil=0;clearHandsFreePhraseBuffer();showHandsFreeHeard('Listening for “Robo-Teacher”…');updateHandsFreeStatus('Listening…');startHandsFreeListening();setLearningStatus('Say “Robo-Teacher” before a command','listening');
}

handsFreeToggle.addEventListener('click',()=>{
  if(!handsFree.enabled){enableHandsFree();return}
  handsFree.enabled=false;handsFree.processing=false;handsFree.pending='';clearHandsFreePhraseBuffer();stopHandsFreeListening();updateHandsFreeStatus();showHandsFreeHeard('');setLearningStatus('Wake-word teaching off');
});

async function ensureSession(){
  if(sessionToken)return sessionToken;
  const profileId=`${learnerClass.value}:${learnerNickname.value.trim().toLocaleLowerCase()}`;
  if(learnerMemoryId!==profileId)loadAdaptiveMemory(profileId);
  let profiles={};
  try{profiles=JSON.parse(localStorage.getItem('roboTeacherProfiles')||'{}')}catch(_){profiles={}}
  let learnerKey=profiles[profileId];
  if(!learnerKey&&Object.keys(profiles).length===0)learnerKey=localStorage.getItem('roboTeacherLearnerKey');
  if(!/^[a-f0-9]{32,64}$/.test(learnerKey||'')){
    const bytes=crypto.getRandomValues(new Uint8Array(24));learnerKey=Array.from(bytes,byte=>byte.toString(16).padStart(2,'0')).join('');
  }
  profiles[profileId]=learnerKey;localStorage.setItem('roboTeacherProfiles',JSON.stringify(profiles));
  localStorage.removeItem('roboTeacherLearnerKey');
  const response=await fetch('/api/classroom/session',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({learner_key:learnerKey,nickname:learnerNickname.value.trim(),class_level:learnerClass.value})});
  if(!response.ok)throw new Error('session');
  const data=await response.json();
  sessionToken=data.session_token;
  return sessionToken;
}

start.addEventListener('click',async()=>{
  const nickname=learnerNickname.value.trim();
  if(nickname.length<2){onboardingError.textContent='Please enter a nickname with at least 2 letters.';onboardingError.classList.remove('hidden');learnerNickname.focus();return}
  onboardingError.classList.add('hidden');start.disabled=true;start.textContent='Opening classroom…';
  try{
    stopFounderSpeech();
    await ensureSession();learnerIdentity.textContent=`${nickname.toUpperCase()} · ${learnerClass.value} CLASSROOM`;
    welcome.classList.add('hidden');classroom.classList.remove('hidden');
    addMessage(`Welcome, ${nickname}! I’ll explain each lesson at ${learnerClass.value} level.`,'teacher');question.focus();
  }catch(_){onboardingError.textContent='I could not start the classroom connection. Please try again.';onboardingError.classList.remove('hidden')}
  finally{start.disabled=false;start.textContent='Start Learning Now →'}
});

showTeacherLogin.addEventListener('click',()=>{teacherLogin.classList.toggle('hidden');if(!teacherLogin.classList.contains('hidden'))teacherAccessKey.focus()});

openTeacherDashboardButton.addEventListener('click',async()=>{
  const accessKey=teacherAccessKey.value.trim();
  if(accessKey.length<16){teacherLoginError.textContent='Enter the private teacher access key.';teacherLoginError.classList.remove('hidden');teacherAccessKey.focus();return}
  teacherLoginError.classList.add('hidden');openTeacherDashboardButton.disabled=true;openTeacherDashboardButton.textContent='Opening…';
  try{teacherClass.value=learnerClass.value;teacherDashboardAccessKey=accessKey;const data=await fetchTeacherDashboard(accessKey);welcome.classList.add('hidden');classroom.classList.remove('hidden');learnerIdentity.textContent=`TEACHER DASHBOARD · ${teacherClass.value}`;showTeacherDashboard(data)}
  catch(error){teacherLoginError.textContent=error.message;teacherLoginError.classList.remove('hidden');teacherAccessKey.focus()}
  finally{openTeacherDashboardButton.disabled=false;openTeacherDashboardButton.textContent='Open Dashboard →';teacherAccessKey.value=''}
});
teacherAccessKey.addEventListener('keydown',event=>{if(event.key==='Enter')openTeacherDashboardButton.click()});

changeLearnerButton.addEventListener('click',()=>{
  stopTeacherAudio();handsFree.enabled=false;handsFree.processing=false;stopHandsFreeListening();updateHandsFreeStatus();sessionToken=null;currentProgress=null;learnerNickname.value='';learnerClass.value='JSS2';practiceClass.value='JSS2';updatePracticeTopics();classroom.classList.add('hidden');welcome.classList.remove('hidden');teacherLogin.classList.add('hidden');onboardingError.classList.add('hidden');learnerNickname.focus();
});

toggle.addEventListener('click',()=>{
  const mini=teacherPanel.classList.toggle('minimized');
  classroom.classList.toggle('teacher-min',mini);
  toggle.textContent=mini?'Show':'Hide';
  toggle.setAttribute('aria-label',mini?'Maximize teacher':'Minimize teacher');
  toggle.setAttribute('aria-expanded',String(!mini));
});

function prepareSpeechText(text){
  return text
    .replace(/\*\*/g,'')
    .replace(/\s*\n+\s*/g,'. ')
    .replace(/\s*([=:])\s*/g,' $1 ')
    .replace(/\s+/g,' ')
    .replace(/([A-Za-zÀ-ž0-9])$/u,'$1.')
    .trim();
}

function setTeacherSpeaking(speaking){
  teacherPanel.classList.toggle('speaking',speaking);
  if(speaking)startAvatarMotion(teacherPanel);else stopAvatarMotion(teacherPanel);
  if(speaking)teacherPanel.classList.remove('paused');
  teacherVoiceStatus.textContent=speaking?'Speaking…':'Ready';
  if(showVoiceAnswerAvatar)canvasVoiceAvatarStatus.textContent=speaking?'Speaking':'Ready';
  readAnswerButton.innerHTML=speaking?'<span>Pause</span>':'<span>Read answer</span>';
  readAnswerButton.setAttribute('aria-label',speaking?'Pause reading the answer':'Read the current answer aloud');
  if(speaking)setLearningStatus('Speaking','speaking');
}

async function pauseTeacherAudio(){
  if(!teacherAudioContext||teacherSpeechPaused)return;
  // Lock the state before suspension so a final streamed chunk cannot close
  // the audio context while the learner is pausing it.
  teacherSpeechPaused=true;
  teacherPanel.classList.remove('speaking');teacherPanel.classList.add('paused');teacherVoiceStatus.textContent='Paused';
  if(showVoiceAnswerAvatar)canvasVoiceAvatarStatus.textContent='Paused';
  stopAvatarMotion(teacherPanel);
  readAnswerButton.innerHTML='<span>Continue</span>';readAnswerButton.setAttribute('aria-label','Continue reading the answer');setLearningStatus('Audio paused','paused');
  try{await teacherAudioContext.suspend()}
  catch(_error){teacherSpeechPaused=false;setTeacherSpeaking(true)}
}

async function resumeTeacherAudio(){
  if(!teacherAudioContext||!teacherSpeechPaused)return;
  try{
    await teacherAudioContext.resume();
    if(teacherAudioContext.state!=='running')throw new Error('audio context did not resume');
    teacherSpeechPaused=false;setTeacherSpeaking(true);
    if(teacherStreamComplete&&!teacherAudioSources.size)stopTeacherAudio();
  }catch(_error){
    teacherSpeechPaused=false;stopTeacherAudio();
    addMessage('I could not continue that audio. Please tap Read answer to try again.','teacher');
  }
}

function stopAudioKeepAlive(){
  if(!teacherAudioKeepAlive)return;
  try{teacherAudioKeepAlive.oscillator.stop()}catch(_error){/* Already stopped. */}
  teacherAudioKeepAlive=null;
}

function ensureAvatarAnalyser(context){
  if(teacherAudioAnalyser)return teacherAudioAnalyser;
  teacherAudioAnalyser=context.createAnalyser();teacherAudioAnalyser.fftSize=256;teacherAudioAnalyser.smoothingTimeConstant=.38;teacherAudioAnalyser.connect(context.destination);return teacherAudioAnalyser;
}

function resetAvatarRig(rig){
  if(!rig)return;rig.classList.remove('avatar-speaking');
  rig.style.setProperty('--mouth-open','0');rig.style.setProperty('--head-x','0px');rig.style.setProperty('--head-y','0px');rig.style.setProperty('--head-turn','0deg');rig.style.setProperty('--breath','1');
}

function setCanvasVoiceAvatar(visible){
  showVoiceAnswerAvatar=visible;
  if(!visible)resetAvatarRig(canvasVoiceAvatar);
  canvasVoiceAvatar.classList.toggle('hidden',!visible);
  canvasWork.classList.toggle('voice-avatar-visible',visible);
}

function stopAvatarMotion(rig=activeAvatarRig){
  if(rig&&activeAvatarRig&&rig!==activeAvatarRig){resetAvatarRig(rig);return}
  if(avatarMotionFrame){cancelAnimationFrame(avatarMotionFrame);avatarMotionFrame=null}
  const stoppedRig=activeAvatarRig||rig;
  resetAvatarRig(stoppedRig);
  if(stoppedRig===teacherPanel)resetAvatarRig(canvasVoiceAvatar);
  activeAvatarRig=null;avatarEnergy=0;
}

function startAvatarMotion(rig){
  if(!rig||!teacherAudioAnalyser)return;
  if(activeAvatarRig!==rig)stopAvatarMotion();activeAvatarRig=rig;rig.classList.add('avatar-speaking');
  const samples=new Uint8Array(teacherAudioAnalyser.fftSize);const started=performance.now();
  const update=now=>{
    if(activeAvatarRig!==rig)return;
    teacherAudioAnalyser.getByteTimeDomainData(samples);let energy=0;
    for(const sample of samples){const level=(sample-128)/128;energy+=level*level}
    const rms=Math.sqrt(energy/samples.length);const target=Math.max(0,Math.min(1,(rms-.012)*8.5));
    avatarEnergy+=(target>avatarEnergy ? .58 : .2)*(target-avatarEnergy);
    const pulse=.86+.14*Math.sin(now*.041);const mouth=Math.round(Math.max(0,Math.min(1,avatarEnergy*pulse))*120)/120;
    const motion=.55+.45*avatarEnergy;
    const nod=Math.sin(now*.0047)*1.8*motion;
    const turn=Math.sin(now*.0029)*1.2*motion;
    rig.style.setProperty('--mouth-open',mouth.toFixed(3));
    rig.style.setProperty('--head-y',`${nod.toFixed(2)}px`);
    rig.style.setProperty('--head-turn',`${turn.toFixed(2)}deg`);
    if(rig===teacherPanel&&showVoiceAnswerAvatar){
      canvasVoiceAvatar.style.setProperty('--mouth-open',mouth.toFixed(3));
      canvasVoiceAvatar.style.setProperty('--head-y',`${nod.toFixed(2)}px`);
      canvasVoiceAvatar.style.setProperty('--head-turn',`${turn.toFixed(2)}deg`);
    }
    avatarMotionFrame=requestAnimationFrame(update);
  };
  avatarMotionFrame=requestAnimationFrame(update);
}

async function startAudioKeepAlive(){
  const context=await prepareTeacherAudio();
  stopAudioKeepAlive();
  const oscillator=context.createOscillator();const gain=context.createGain();gain.gain.value=.00001;
  oscillator.connect(gain);gain.connect(context.destination);oscillator.start();teacherAudioKeepAlive={oscillator,gain};
}

function stopTeacherAudio(preserveAudioUnlock=false){
  teacherSpeechRequest+=1;
  if(teacherSpeechController){teacherSpeechController.abort();teacherSpeechController=null}
  if(!preserveAudioUnlock)stopAudioKeepAlive();
  teacherAudioSources.forEach(source=>{try{source.stop()}catch(_error){/* Already stopped. */}});teacherAudioSources.clear();
  teacherStreamComplete=false;
  teacherSpeechPaused=false;
  teacherPanel.classList.remove('paused');
  setTeacherSpeaking(false);
  setCanvasVoiceAvatar(false);
  readAnswerButton.disabled=!canvasAnswer.textContent.trim();
}

async function prepareTeacherAudio(){
  const AudioContextClass=window.AudioContext||window.webkitAudioContext;
  if(!AudioContextClass)throw new Error('Web Audio is unavailable');
  if(!teacherAudioContext||teacherAudioContext.state==='closed')teacherAudioContext=new AudioContextClass({sampleRate:24000});
  if(teacherAudioContext.state==='suspended')await teacherAudioContext.resume();
  ensureAvatarAnalyser(teacherAudioContext);
  return teacherAudioContext;
}

async function playPcmStream(response,requestId){
  const context=await prepareTeacherAudio();const reader=response.body.getReader();let pending=new Uint8Array(0);let nextStart=context.currentTime+.06;let receivedAudio=false;
  const finishIfDone=()=>{if(teacherStreamComplete&&!teacherAudioSources.size&&!teacherSpeechPaused&&requestId===teacherSpeechRequest)stopTeacherAudio()};
  while(requestId===teacherSpeechRequest){
    const {done,value}=await reader.read();if(done)break;
    const joined=new Uint8Array(pending.length+value.length);joined.set(pending);joined.set(value,pending.length);
    const evenLength=joined.length-joined.length%2;pending=joined.slice(evenLength);
    if(!evenLength)continue;
    if(!receivedAudio){
      receivedAudio=true;
      stopAudioKeepAlive();
      readAnswerButton.disabled=false;
      setTeacherSpeaking(true);
    }
    const samples=evenLength/2;const buffer=context.createBuffer(1,samples,24000);const channel=buffer.getChannelData(0);const view=new DataView(joined.buffer,joined.byteOffset,evenLength);
    for(let index=0;index<samples;index++)channel[index]=view.getInt16(index*2,true)/32768;
    const source=context.createBufferSource();source.buffer=buffer;source.connect(ensureAvatarAnalyser(context));teacherAudioSources.add(source);
    source.addEventListener('ended',()=>{teacherAudioSources.delete(source);finishIfDone()},{once:true});
    const startAt=Math.max(nextStart,context.currentTime+.025);source.start(startAt);nextStart=startAt+buffer.duration;
  }
  if(requestId===teacherSpeechRequest&&!receivedAudio)throw new Error('empty voice stream');
  teacherStreamComplete=true;finishIfDone();
}

async function requestTeacherSpeech(payload,signal,requestId){
  let response;
  for(let attempt=0;attempt<3;attempt++){
    response=await fetch('/api/classroom/speech',{method:'POST',headers:{'Content-Type':'application/json','Accept':'audio/L16'},body:JSON.stringify(payload),signal});
    if(response.ok||response.status===401||![429,503].includes(response.status))return response;
    if(attempt<2){
      teacherVoiceStatus.textContent='Voice busy — retrying…';
      canvasVoiceAvatarStatus.textContent='Preparing';
      setLearningStatus('Natural voice is busy — retrying','thinking');
      await new Promise(resolve=>setTimeout(resolve,900*(attempt+1)));
      if(requestId!==teacherSpeechRequest)throw new DOMException('Speech cancelled','AbortError');
    }
  }
  return response;
}

async function speakText(text,preserveAudioUnlock=false,displayCanvasAvatar=true){
  if(!text.trim())return;
  stopTeacherAudio(preserveAudioUnlock);
  setCanvasVoiceAvatar(displayCanvasAvatar);
  teacherVoiceStatus.textContent='Preparing teacher voice…';
  readAnswerButton.disabled=true;
  readAnswerButton.innerHTML='<span>Preparing…</span>';
  readAnswerButton.setAttribute('aria-label','Preparing the teacher voice');
  setLearningStatus('Preparing teacher voice','thinking');
  const requestId=teacherSpeechRequest;
  teacherSpeechController=new AbortController();
  try{
    if(!preserveAudioUnlock||!teacherAudioKeepAlive)await startAudioKeepAlive();
    const token=await ensureSession();
    if(requestId!==teacherSpeechRequest)return;
    const response=await requestTeacherSpeech({text:prepareSpeechText(text),session_token:token,language:language.value,voice_gender:teacherPanel.dataset.voiceGender==='male'?'male':'female'},teacherSpeechController.signal,requestId);
    if(response.status===401){sessionToken=null;throw new Error('session')}
    if(!response.ok)throw new Error('natural voice unavailable');
    if(!response.body)throw new Error('stream unavailable');
    await playPcmStream(response,requestId);
  }catch(error){
    if(error.name==='AbortError'||requestId!==teacherSpeechRequest)return;
    stopTeacherAudio();
    readAnswerButton.disabled=!canvasAnswer.textContent.trim();
    addMessage('The natural teacher voice is temporarily unavailable. You can continue reading the worked answer on the Teaching Canvas.','teacher');
  }
}

readAnswerButton.addEventListener('click',async()=>{
  if(teacherSpeechPaused){await resumeTeacherAudio();return;}
  if(teacherPanel.classList.contains('speaking')){await pauseTeacherAudio();return;}
  try{await prepareTeacherAudio()}catch(_error){return}
  void speakText(canvasAnswer.textContent);
});

function stopFounderSpeech(){
  founderSpeechRequest+=1;if(founderSpeechController){founderSpeechController.abort();founderSpeechController=null}
  founderAudioSources.forEach(source=>{try{source.stop()}catch(_error){/* Already stopped. */}});founderAudioSources.clear();founderStreamComplete=false;stopAvatarMotion(founderPanel);hearFounderButton.disabled=false;hearFounderButton.textContent='Hear Herbert';
}

async function playFounderPcmStream(response,requestId){
  const context=await prepareTeacherAudio();const reader=response.body.getReader();let pending=new Uint8Array(0);let nextStart=context.currentTime+.06;let received=false;founderStreamComplete=false;
  while(requestId===founderSpeechRequest){const {done,value}=await reader.read();if(done)break;const joined=new Uint8Array(pending.length+value.length);joined.set(pending);joined.set(value,pending.length);const evenLength=joined.length-joined.length%2;pending=joined.slice(evenLength);if(!evenLength)continue;
    if(!received){received=true;hearFounderButton.disabled=false;hearFounderButton.textContent='Stop Herbert';startAvatarMotion(founderPanel)}
    const samples=evenLength/2;const buffer=context.createBuffer(1,samples,24000);const channel=buffer.getChannelData(0);const view=new DataView(joined.buffer,joined.byteOffset,evenLength);for(let index=0;index<samples;index++)channel[index]=view.getInt16(index*2,true)/32768;
    const source=context.createBufferSource();source.buffer=buffer;source.connect(ensureAvatarAnalyser(context));founderAudioSources.add(source);source.addEventListener('ended',()=>{founderAudioSources.delete(source);if(requestId===founderSpeechRequest&&founderStreamComplete&&!founderAudioSources.size)stopFounderSpeech()},{once:true});const startAt=Math.max(nextStart,context.currentTime+.025);source.start(startAt);nextStart=startAt+buffer.duration;
  }
  if(requestId===founderSpeechRequest&&!received)throw new Error('empty voice stream');
  founderStreamComplete=true;if(requestId===founderSpeechRequest&&!founderAudioSources.size)stopFounderSpeech();
}

hearFounderButton.addEventListener('click',async()=>{
  if(founderAudioSources.size||founderPanel.classList.contains('avatar-speaking')){stopFounderSpeech();return}
  if(learnerNickname.value.trim().length<2){onboardingError.textContent='Enter your nickname first, then tap Hear Herbert.';onboardingError.classList.remove('hidden');learnerNickname.focus();return}
  onboardingError.classList.add('hidden');hearFounderButton.disabled=true;hearFounderButton.textContent='Preparing Herbert…';const requestId=++founderSpeechRequest;founderSpeechController=new AbortController();
  try{await prepareTeacherAudio();const token=await ensureSession();if(requestId!==founderSpeechRequest)return;const intro=`Hello ${learnerNickname.value.trim()}. I am Herbert, the founder of Robo-Teacher. Welcome to your AI classroom. Choose your class, then tap Start Learning Now.`;const response=await fetch('/api/classroom/speech',{method:'POST',headers:{'Content-Type':'application/json','Accept':'audio/L16'},body:JSON.stringify({text:intro,session_token:token,language:'English',voice_gender:'male'}),signal:founderSpeechController.signal});if(!response.ok||!response.body)throw new Error('voice unavailable');await playFounderPcmStream(response,requestId)}catch(error){if(error.name!=='AbortError'&&requestId===founderSpeechRequest){onboardingError.textContent='Herbert’s natural voice is temporarily unavailable. Please try again later.';onboardingError.classList.remove('hidden')}stopFounderSpeech()}
});

function addMessage(text,role){
  const el=document.createElement('div');el.className=`message ${role}`;el.textContent=text;
  messages.appendChild(el);messages.scrollTop=messages.scrollHeight;return el;
}

function setLearningStatus(message,state=''){
  learningStatus.textContent=message;learningStatus.dataset.state=state;
  teachingCanvas.setAttribute('aria-busy',String(state==='thinking'));
}

function setActiveMode(button){
  document.querySelectorAll('.class-tools [data-mode]').forEach(item=>{
    const active=item===button;item.classList.toggle('active',active);
    if(active)item.setAttribute('aria-current','page');else item.removeAttribute('aria-current');
  });
}

function openChat(){
  dismissLessonOverlays();
  whiteboardArea.classList.add('hidden');practiceArea.classList.add('hidden');progressArea.classList.add('hidden');teacherDashboard.classList.add('hidden');qaChecklist.classList.add('hidden');
  if(canvasAnswer.textContent.trim())canvasWork.classList.remove('hidden');else canvasEmpty.classList.remove('hidden');
  setActiveMode(chatButton);setLearningStatus('Ready to learn');question.focus();
}

function showCanvasAnswer(answer,status='Worked solution',preserveAudioUnlock=false){
  // A newly displayed solution always replaces any playing or paused answer.
  stopTeacherAudio(preserveAudioUnlock);
  dismissLessonOverlays();restoreTeacherPanel();
  whiteboardArea.classList.add('hidden');practiceArea.classList.add('hidden');progressArea.classList.add('hidden');canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');
  canvasStatus.textContent=status;startLessonDirector(answer);
  readAnswerButton.disabled=!answer.trim();setActiveMode(chatButton);setLearningStatus('Answer ready');
  keepTeachingCanvasVisible();
}

function keepTeachingCanvasVisible(){
  if(document.activeElement===question)question.blur();
  setTimeout(()=>teachingCanvas.scrollIntoView({block:'start',behavior:'smooth'}),220);
}

function splitLessonSteps(text){
  const blocks=text.trim().split(/\n\s*\n|(?=\bStep\s+\d+\s*[:.-])/i).map(item=>item.trim()).filter(Boolean);
  if(blocks.length>1)return blocks;
  const lines=text.trim().split(/\n+/).map(item=>item.trim()).filter(Boolean);
  return lines.length>1?lines:[text.trim()];
}

function renderLessonBlock(container,text){
  container.replaceChildren();
  const paragraph=document.createElement('p');
  text.split('\n').forEach((line,lineIndex)=>{
    if(lineIndex)paragraph.appendChild(document.createElement('br'));
    line.split('**').forEach((part,index)=>{
      const node=index%2?document.createElement('strong'):document.createTextNode(part);
      if(index%2)node.textContent=part;
      paragraph.appendChild(node);
    });
  });
  container.appendChild(paragraph);
}

function startLessonDirector(text,index=0){
  const steps=splitLessonSteps(text);
  currentLesson={text,steps,index:Math.max(0,Math.min(index,steps.length-1))};
  lessonChoreography.visited.clear();
  lessonDirector.classList.remove('hidden');
  setTeachingStageMode('lesson');
  renderCurrentLessonStep();
}

function chooseTeachingMode(step,index,total){
  const text=step.toLowerCase();
  if(adaptiveSupportLevel()==='support'&&index>0)return {mode:'example',label:'Teaching memory recommends an extra worked example'};
  if(adaptiveSupportLevel()==='challenge'&&index===total-1)return {mode:'check',label:'Teaching memory recommends a challenge check'};
  if(/plot|graph|diagram|shape|angle|coordinate|number line|fraction|triangle|circle|area|perimeter/.test(text))return {mode:'visual',label:'A visual will make this step clearer'};
  if(index===total-1)return {mode:'check',label:'A quick check will confirm understanding'};
  if(/example|calculate|solve|work out|multiply|divide|subtract|add|equation|=|\d/.test(text))return {mode:'example',label:'A worked example will help with this step'};
  return {mode:'lesson',label:'Read and discuss this explanation'};
}

function scheduleLessonChoreography(){
  clearTimeout(lessonChoreography.timer);
  if(!currentLesson)return;
  const {steps,index}=currentLesson;
  const choice=chooseTeachingMode(steps[index],index,steps.length);
  lessonChoreographyHint.textContent=`Recommended: ${choice.label}.`;
  showStepVisual.classList.toggle('recommended',choice.mode==='visual');
  watchStepExample.classList.toggle('recommended',choice.mode==='example');
  checkStepUnderstanding.classList.toggle('recommended',choice.mode==='check');
  if(!lessonChoreography.enabled||choice.mode==='lesson')return;
  const key=`${currentLesson.text}\u0000${index}\u0000${choice.mode}`;
  if(lessonChoreography.visited.has(key))return;
  lessonChoreography.visited.add(key);
  lessonChoreography.timer=setTimeout(()=>{
    if(!lessonChoreography.enabled||!currentLesson||currentLesson.index!==index||lessonInterruption)return;
    if(choice.mode==='visual')showVisualExplanation();
    else if(choice.mode==='example')openLessonMedia();
    else if(choice.mode==='check')startUnderstandingCheck();
  },650);
}

autoTeachToggle.addEventListener('click',()=>{
  lessonChoreography.enabled=!lessonChoreography.enabled;
  autoTeachToggle.setAttribute('aria-pressed',String(lessonChoreography.enabled));
  autoTeachToggle.textContent=`Auto Teach: ${lessonChoreography.enabled?'On':'Off'}`;
  setLearningStatus(`Automatic teaching ${lessonChoreography.enabled?'on':'off'}`);
  if(lessonChoreography.enabled)scheduleLessonChoreography();else clearTimeout(lessonChoreography.timer);
});

function setTeachingStageMode(mode){
  const labels={lesson:'Lesson',visual:'Visual',example:'Example',check:'Check'};
  teachingStage.mode=mode;teachingCanvas.dataset.stageMode=mode;
  teachingStageMode.textContent=labels[mode]||'Lesson';
}

function enterTeachingStage(mode){
  teachingStage.bookmark=currentLesson?.index||0;setTeachingStageMode(mode);setCanvasVoiceAvatar(false);
  teacherPanel.classList.add('minimized');classroom.classList.add('teacher-min');toggle.textContent='Show';toggle.setAttribute('aria-expanded','false');
}

function restoreTeachingStage(){
  setTeachingStageMode('lesson');
  if(currentLesson){currentLesson.index=Math.min(teachingStage.bookmark,currentLesson.steps.length-1);renderCurrentLessonStep();canvasWork.classList.remove('hidden');canvasEmpty.classList.add('hidden')}
  else if(canvasAnswer.textContent.trim())canvasWork.classList.remove('hidden');else canvasEmpty.classList.remove('hidden');
  restoreTeacherPanel();setLearningStatus(`Returned to lesson step ${(currentLesson?.index||0)+1}`);
}

function renderCurrentLessonStep(){
  if(!currentLesson)return;
  const {steps,index}=currentLesson;
  renderLessonBlock(canvasAnswer,steps[index]);
  lessonStepLabel.textContent=`Step ${index+1} of ${steps.length}`;
  lessonStepTrack.replaceChildren();
  steps.forEach((_step,stepIndex)=>{const marker=document.createElement('i');marker.classList.toggle('active',stepIndex===index);marker.classList.toggle('complete',stepIndex<index);lessonStepTrack.appendChild(marker)});
  previousLessonStep.disabled=index===0;
  nextLessonStep.disabled=index===steps.length-1;
  nextLessonStep.textContent=index===steps.length-1?'Lesson complete':'Next →';
  returnToLesson.classList.toggle('hidden',!lessonHistory.length);
  lessonPauseNotice.classList.toggle('hidden',!lessonInterruption);
  askLessonQuestion.textContent=lessonInterruption?'Continue this step':'Ask about this step';
  readAnswerButton.disabled=!steps[index].trim();
  canvasAnswer.scrollIntoView({block:'nearest',behavior:'smooth'});
  scheduleLessonChoreography();
}

function moveLessonStep(direction){
  if(!currentLesson)return;stopTeacherAudio();lessonInterruption=null;
  currentLesson.index=Math.max(0,Math.min(currentLesson.steps.length-1,currentLesson.index+direction));
  renderCurrentLessonStep();setLearningStatus(`Lesson step ${currentLesson.index+1} ready`);
}

previousLessonStep.addEventListener('click',()=>moveLessonStep(-1));
nextLessonStep.addEventListener('click',()=>moveLessonStep(1));
replayLessonStep.addEventListener('click',()=>{if(currentLesson){recordLearningSignal('replays');void speakText(currentLesson.steps[currentLesson.index])}});
showStepVisual.addEventListener('click',showVisualExplanation);
watchStepExample.addEventListener('click',openLessonMedia);
checkStepUnderstanding.addEventListener('click',startUnderstandingCheck);
function pauseLessonForQuestion(source='text'){
  if(!currentLesson)return;
  if(!lessonInterruption){lessonInterruption={text:currentLesson.text,index:currentLesson.index};recordLearningSignal('questions')}
  stopTeacherAudio();
  lessonPauseNotice.textContent=`Lesson paused at Step ${currentLesson.index+1}. Ask your question ${source==='voice'?'using the microphone':'below'}.`;
  lessonPauseNotice.classList.remove('hidden');askLessonQuestion.textContent='Continue this step';lessonDirector.classList.add('lesson-paused');
  setLearningStatus('Lesson paused for your question','paused');
}
askLessonQuestion.addEventListener('click',()=>{
  if(lessonInterruption){lessonInterruption=null;lessonDirector.classList.remove('lesson-paused');renderCurrentLessonStep();setLearningStatus(`Lesson step ${currentLesson.index+1} resumed`);return}
  pauseLessonForQuestion();question.placeholder='Ask a question about this step…';question.focus();
});
returnToLesson.addEventListener('click',()=>{if(!lessonHistory.length)return;stopTeacherAudio();lessonInterruption=null;lessonDirector.classList.remove('lesson-paused');const lesson=lessonHistory.pop();startLessonDirector(lesson.text,lesson.index);canvasStatus.textContent='Previous lesson resumed';setLearningStatus('Returned to your lesson')});
endLesson.addEventListener('click',()=>{stopTeacherAudio();currentLesson=null;lessonInterruption=null;lessonHistory.length=0;lessonDirector.classList.add('hidden');lessonDirector.classList.remove('lesson-paused');canvasWork.classList.add('hidden');canvasEmpty.classList.remove('hidden');canvasAnswer.replaceChildren();readAnswerButton.disabled=true;question.placeholder='Ask your teacher a question…';setLearningStatus('Lesson ended')});

function renderLesson(container,text){
  renderLessonBlock(container,text);
}

uploadButton.addEventListener('click',()=>imageUpload.click());
cameraButton.addEventListener('click',()=>cameraCapture.click());
imageUpload.addEventListener('change',()=>handleImage(imageUpload.files[0]));
cameraCapture.addEventListener('change',()=>handleImage(cameraCapture.files[0]));
micButton.addEventListener('click',toggleRecording);
simplifyButton.addEventListener('click',simplifyCurrentAnswer);
understandingButton.addEventListener('click',startUnderstandingCheck);
visualButton.addEventListener('click',showVisualExplanation);
closeVisualButton.addEventListener('click',closeVisualExplanation);
mediaButton.addEventListener('click',openLessonMedia);
closeMediaButton.addEventListener('click',closeLessonMedia);
understandingForm.addEventListener('submit',submitUnderstandingAnswer);
closeUnderstandingButton.addEventListener('click',closeUnderstandingCheck);
whiteboardButton.addEventListener('click',openWhiteboard);
closeBoardButton.addEventListener('click',closeWhiteboard);
penTool.addEventListener('click',()=>selectDrawingTool('pen'));
eraserTool.addEventListener('click',()=>selectDrawingTool('eraser'));
clearBoardButton.addEventListener('click',clearWhiteboard);
submitBoardButton.addEventListener('click',submitWhiteboard);
whiteboard.addEventListener('pointerdown',startDrawing);
whiteboard.addEventListener('pointermove',drawOnWhiteboard);
whiteboard.addEventListener('pointerup',stopDrawing);
whiteboard.addEventListener('pointercancel',stopDrawing);
backToWhiteboard.addEventListener('click',openWhiteboard);
language.addEventListener('change',async()=>{
  const wasReading=teacherPanel.classList.contains('speaking')||teacherSpeechPaused;
  const answerToTranslate=canvasAnswer.textContent.trim();
  stopTeacherAudio();
  if(wasReading){try{await startAudioKeepAlive()}catch(_error){/* Translation still works without automatic audio. */}}
  const switchId=++languageSwitchRequest;
  localStorage.setItem('roboTeacherLanguage',language.value);
  const notices={English:'I will teach you in English from now on.',Yoruba:'Mo máa kọ́ ọ ní Yorùbá láti ìsinsin yìí.',Igbo:'Aga m akụziri gị ihe n’Igbo site ugbu a.',Hausa:'Zan koyar da kai da Hausa daga yanzu.'};
  addMessage(notices[language.value],'teacher');
  if(currentPractice)await switchPracticeLanguage();
  if(answerToTranslate){
    setLearningStatus(`Switching explanation to ${language.options[language.selectedIndex].text}…`,'thinking');
    readAnswerButton.disabled=true;
    try{
      const token=await ensureSession();
      const response=await fetch('/api/classroom/translate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:answerToTranslate,session_token:token,language:language.value})});
      const data=await response.json();
      if(switchId!==languageSwitchRequest)return;
      if(response.status===401){sessionToken=null;throw new Error('session')}
      if(!response.ok)throw new Error(data.detail||'translation');
      startLessonDirector(data.translation,currentLesson?.index||0);readAnswerButton.disabled=false;
      canvasStatus.textContent=`Explanation switched to ${language.options[language.selectedIndex].text}`;
      setLearningStatus('Explanation ready');
      if(wasReading)void speakText(data.translation,true);
    }catch(error){
      if(switchId!==languageSwitchRequest)return;
      stopAudioKeepAlive();
      readAnswerButton.disabled=false;setLearningStatus('Language switch needs another try','attention');
      addMessage(error.message&&!['translation','session'].includes(error.message)?error.message:'I could not switch the current explanation. Please change the language again.','teacher');
    }
  }
  if(currentProgress&&!progressArea.classList.contains('hidden'))renderProgress(currentProgress);
  if(currentTeacherDashboard&&!teacherDashboard.classList.contains('hidden'))renderTeacherDashboard(currentTeacherDashboard);
  question.focus();
});
languageButton.addEventListener('click',()=>language.focus());
chatButton.addEventListener('click',openChat);
practiceButton.addEventListener('click',openPractice);
startPracticeButton.addEventListener('click',startPracticeSession);
startDiagnosticButton.addEventListener('click',startDiagnosticSession);
practiceForm.addEventListener('submit',submitPracticeAnswer);
showHintButton.addEventListener('click',showPracticeHint);
nextPracticeButton.addEventListener('click',loadNextPracticeQuestion);
closePracticeButton.addEventListener('click',closePractice);
practiceAgainButton.addEventListener('click',startPracticeSession);
changePracticeTopicButton.addEventListener('click',openResultRecommendation);
exitPracticeResultsButton.addEventListener('click',closePractice);
progressButton.addEventListener('click',openProgress);
teacherDashboardButton.addEventListener('click',openTeacherDashboard);
closeTeacherDashboard.addEventListener('click',()=>{teacherDashboard.classList.add('hidden');canvasEmpty.classList.remove('hidden')});
teacherClass.addEventListener('change',refreshTeacherDashboard);
downloadTeacherReport.addEventListener('click',downloadTeacherDashboardReport);
openQaChecklist.addEventListener('click',showQaChecklist);
closeQaChecklist.addEventListener('click',()=>{qaChecklist.classList.add('hidden');teacherDashboard.classList.remove('hidden')});
downloadQaReport.addEventListener('click',downloadQaChecklistReport);
viewProgressFromResults.addEventListener('click',openProgress);
closeProgressButton.addEventListener('click',closeProgress);
emptyStartPractice.addEventListener('click',openPracticeFromProgress);
practiceRecommendation.addEventListener('click',openRecommendedPractice);
learningPath.addEventListener('click',event=>{const button=event.target.closest('button[data-topic]');if(button)openLearningPathTopic(button.dataset.term,button.dataset.topic)});

function openPractice(){
  whiteboardArea.classList.add('hidden');progressArea.classList.add('hidden');canvasWork.classList.add('hidden');canvasEmpty.classList.add('hidden');practiceArea.classList.remove('hidden');setActiveMode(practiceButton);setLearningStatus('Practice Mode');
  if(currentPracticeSummary)renderPracticeResults(currentPracticeSummary);
  else if(currentPractice){practiceSetup.classList.add('hidden');practiceQuestion.classList.remove('hidden');practiceResults.classList.add('hidden');practiceAnswer.focus()}
  else resetPracticeSetup();
}

function closePractice(){
  practiceArea.classList.add('hidden');
  if(canvasAnswer.textContent.trim())canvasWork.classList.remove('hidden');else canvasEmpty.classList.remove('hidden');setActiveMode(chatButton);setLearningStatus('Ready to learn');
}

function renderPracticeQuestion(data){
  currentPractice=data;currentPracticeSummary=null;practiceSetup.classList.add('hidden');practiceResults.classList.add('hidden');practiceQuestion.classList.remove('hidden');
  practiceProgress.textContent=`Question ${data.question_number} of ${data.total_questions}`;practiceScore.textContent=`Score: ${data.score}/${data.attempted}`;
  practiceContext.textContent=`${data.class_level} · ${data.topic} · ${data.difficulty}`;practicePrompt.textContent=data.question;
  practiceAnswer.value='';practiceAnswer.disabled=false;practiceForm.querySelector('button').disabled=false;
  practiceFeedback.textContent='';practiceFeedback.className='practice-feedback hidden';showHintButton.disabled=false;
  showHintButton.textContent='Show Hint';nextPracticeButton.textContent='Next Question →';nextPracticeButton.classList.add('hidden');setLearningStatus(`Question ${data.question_number} of ${data.total_questions}`);practiceAnswer.focus();
}

async function practiceRequest(path,body){
  const token=await ensureSession();
  const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),20000);
  try{
    const response=await fetch(`/api/classroom/practice/${path}`,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({session_token:token,...body}),signal:controller.signal});
    let data={};try{data=await response.json()}catch(_error){/* Use the friendly fallback below. */}
    if(response.status===401)sessionToken=null;if(!response.ok)throw new Error(data.detail||'Practice request failed. Please try again.');return data;
  }catch(error){if(error.name==='AbortError')throw new Error('The connection took too long. Please try again.');throw error}
  finally{clearTimeout(timeout)}
}

async function diagnosticRequest(path,body){
  const token=await ensureSession();const response=await fetch(`/api/classroom/diagnostic/${path}`,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({session_token:token,...body})});const data=await response.json();if(!response.ok)throw new Error(data.detail||'Diagnostic request failed.');return data
}

async function startPracticeSession(){
  practiceMode='practice';
  startPracticeButton.disabled=true;practiceAgainButton.disabled=true;startPracticeButton.textContent='Preparing…';setLearningStatus('Preparing your practice','thinking');
  try{renderPracticeQuestion(await practiceRequest('start',{topic:practiceTopic.value,difficulty:practiceDifficulty.value,question_count:Number(practiceCount.value),class_level:practiceClass.value,language:language.value}))}
  catch(err){addMessage(err.message,'teacher')}
  finally{startPracticeButton.disabled=false;practiceAgainButton.disabled=false;startPracticeButton.textContent='Start Practice →';setLearningStatus('Practice ready')}
}

async function startDiagnosticSession(){
  startDiagnosticButton.disabled=true;startDiagnosticButton.textContent='Preparing diagnostic…';practiceMode='diagnostic';
  try{renderPracticeQuestion(await diagnosticRequest('start',{class_level:practiceClass.value,term:practiceTerm.value,language:language.value}))}
  catch(err){addMessage(err.message,'teacher');practiceMode='practice'}
  finally{startDiagnosticButton.disabled=false;startDiagnosticButton.textContent='Take 10-Question Diagnostic'}
}

async function switchPracticeLanguage(){
  const languageNames={English:'English',Yoruba:'Yorùbá',Igbo:'Igbo',Hausa:'Hausa'};
  const selectedLanguage=languageNames[language.value]||language.value;
  language.disabled=true;setLearningStatus(`Switching question to ${selectedLanguage}…`,'thinking');
  try{
    const data=await (practiceMode==='diagnostic'?diagnosticRequest('language',{language:language.value}):practiceRequest('language',{language:language.value}));
    currentPractice={...currentPractice,...data};practicePrompt.textContent=data.question;
    if(data.answered&&data.feedback){
      const feedback=data.feedback;
      practiceFeedback.textContent=feedback.correct?`${feedback.message}\n\n${feedback.explanation}`:`${feedback.message}\n\n${feedback.explanation}\n\n${feedback.correct_answer_label}: ${feedback.expected_answer}`;
      practiceFeedback.className=`practice-feedback ${feedback.correct?'correct':'incorrect'}`;
    }else if(showHintButton.disabled){practiceFeedback.textContent=`Hint: ${data.hint}`}
    if(data.summary){currentPracticeSummary=data.summary;if(!practiceResults.classList.contains('hidden'))renderPracticeResults(data.summary)}
    setLearningStatus(`${selectedLanguage} question ready`);
  }catch(err){addMessage(err.message,'teacher');setLearningStatus('Language switch needs attention','attention')}
  finally{language.disabled=false}
}

function showPracticeHint(){
  if(!currentPractice)return;practiceFeedback.textContent=`Hint: ${currentPractice.hint}`;practiceFeedback.className='practice-feedback';showHintButton.disabled=true;showHintButton.textContent='Hint shown';
}

async function submitPracticeAnswer(event){
  event.preventDefault();const answer=practiceAnswer.value.trim();if(!answer)return;
  const checkButton=practiceForm.querySelector('button');checkButton.disabled=true;setLearningStatus('Checking your answer','thinking');
  try{
    const result=await (practiceMode==='diagnostic'?diagnosticRequest('answer',{answer}):practiceRequest('answer',{answer}));practiceAnswer.disabled=true;
    practiceScore.textContent=`Score: ${result.score}/${result.attempted} (${result.percentage}%)`;
    practiceFeedback.textContent=result.correct?`${result.message}\n\n${result.explanation}`:`${result.message}\n\n${result.explanation}\n\n${result.correct_answer_label}: ${result.expected_answer}`;
    practiceFeedback.className=`practice-feedback ${result.correct?'correct':'incorrect'}`;nextPracticeButton.classList.remove('hidden');showHintButton.disabled=true;
    if(result.completed){currentPracticeSummary=result.summary;nextPracticeButton.textContent='View Results →'}setLearningStatus(result.correct?'Correct answer':'Review the explanation',result.correct?'success':'attention')
  }catch(err){practiceFeedback.textContent=err.message;practiceFeedback.className='practice-feedback incorrect';checkButton.disabled=false}
}

async function loadNextPracticeQuestion(){
  if(currentPracticeSummary){renderPracticeResults(currentPracticeSummary);return}
  nextPracticeButton.disabled=true;
  try{renderPracticeQuestion(await (practiceMode==='diagnostic'?diagnosticRequest('next',{}):practiceRequest('next',{})))}
  catch(err){practiceFeedback.textContent=err.message;practiceFeedback.className='practice-feedback incorrect'}
  finally{nextPracticeButton.disabled=false}
}

function resetPracticeSetup(){
  currentPractice=null;currentPracticeSummary=null;practiceQuestion.classList.add('hidden');practiceResults.classList.add('hidden');practiceSetup.classList.remove('hidden');
}

function renderPracticeResults(summary){
  currentPracticeSummary=summary;practiceSetup.classList.add('hidden');practiceQuestion.classList.add('hidden');practiceResults.classList.remove('hidden');
  const labels=resultCopy[language.value]||resultCopy.English;
  resultPercentage.textContent=`${summary.percentage}%`;resultScore.textContent=labels.score(summary.score,summary.attempted);
  resultRecommendation.textContent=summary.recommendation;missedReview.replaceChildren();
  practiceAgainButton.textContent=labels.again;viewProgressFromResults.textContent=labels.progress;exitPracticeResultsButton.textContent=labels.exit;
  changePracticeTopicButton.textContent=summary.diagnostic?labels.recommended:labels.change;
  if(summary.topic_results){const topicHeading=document.createElement('h4');topicHeading.textContent=labels.diagnostic;missedReview.appendChild(topicHeading);summary.topic_results.forEach(item=>{const row=document.createElement('article');row.textContent=`${item.topic}: ${item.percentage}% (${item.correct}/${item.attempted})`;missedReview.appendChild(row)})}
  const heading=document.createElement('h4');heading.textContent=summary.missed.length?labels.review:labels.perfect;missedReview.appendChild(heading);
  if(!summary.missed.length){const note=document.createElement('p');note.textContent=labels.perfectNote;missedReview.appendChild(note);return}
  summary.missed.forEach((item,index)=>{
    const card=document.createElement('article');
    const title=document.createElement('strong');title.textContent=`${index+1}. ${item.question}`;
    const answers=document.createElement('p');answers.textContent=`${labels.yourAnswer}: ${item.learner_answer || labels.noAnswer} · ${labels.correctAnswer}: ${item.correct_answer}`;
    const explanation=document.createElement('p');explanation.textContent=item.explanation;
    card.append(title,answers,explanation);missedReview.appendChild(card);
  });
}

function openResultRecommendation(){
  const summary=currentPracticeSummary;resetPracticeSetup();
  if(summary?.diagnostic){practiceClass.value=summary.class_level;practiceTerm.value=summary.term;updatePracticeTopics();practiceTopic.value=summary.recommended_topic;practiceDifficulty.value=summary.recommended_difficulty}
}

async function openProgress(){
  whiteboardArea.classList.add('hidden');practiceArea.classList.add('hidden');teacherDashboard.classList.add('hidden');canvasWork.classList.add('hidden');canvasEmpty.classList.add('hidden');progressArea.classList.remove('hidden');setActiveMode(progressButton);setLearningStatus('Loading your progress','thinking');
  progressLoading.classList.remove('hidden');progressEmpty.classList.add('hidden');progressDashboard.classList.add('hidden');
  try{currentProgress=await practiceRequest('progress',{class_level:learnerClass.value});renderProgress(currentProgress)}
  catch(error){progressLoading.textContent=error.message;progressLoading.classList.add('error')}
}

async function openTeacherDashboard(){
  const accessKey=window.prompt('Enter the private teacher access key.');if(!accessKey)return;
  teacherDashboardAccessKey=accessKey;teacherClass.value=learnerClass.value;
  try{await loadTeacherDashboard(accessKey)}catch(error){teacherDashboardContent.textContent=error.message}
}

async function loadTeacherDashboard(accessKey){
  whiteboardArea.classList.add('hidden');practiceArea.classList.add('hidden');progressArea.classList.add('hidden');canvasWork.classList.add('hidden');canvasEmpty.classList.add('hidden');teacherDashboard.classList.remove('hidden');teacherDashboardContent.textContent='Loading class performance…';setActiveMode(teacherDashboardButton);setLearningStatus('Loading Teacher View','thinking');
  showTeacherDashboard(await fetchTeacherDashboard(accessKey))
}

async function fetchTeacherDashboard(accessKey){
  const response=await fetch('/api/classroom/teacher/dashboard',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({access_key:accessKey,class_level:teacherClass.value})});const data=await response.json();if(!response.ok)throw new Error(data.detail||'Teacher dashboard unavailable');return data
}

function showTeacherDashboard(data){
  currentTeacherDashboard=data;whiteboardArea.classList.add('hidden');practiceArea.classList.add('hidden');progressArea.classList.add('hidden');canvasWork.classList.add('hidden');canvasEmpty.classList.add('hidden');teacherDashboard.classList.remove('hidden');renderTeacherDashboard(data);setLearningStatus('Teacher View ready')
}

function renderTeacherDashboard(data){
  teacherDashboardContent.replaceChildren();const stats=document.createElement('div');stats.className='progress-stats';
  [[dcopy('learners'),data.learners],[dcopy('sessions'),data.sessions],[dcopy('questions'),data.questions],[dcopy('average'),`${data.average_percentage}%`]].forEach(([label,value])=>{const card=document.createElement('article');const name=document.createElement('span');name.textContent=label;const score=document.createElement('strong');score.textContent=value;card.append(name,score);stats.appendChild(card)});
  const insight=document.createElement('div');insight.className='teacher-insights';
  [[dcopy('strongest'),data.strongest_topic||dcopy('noData')],[dcopy('weakest'),data.weakest_topic||dcopy('noData')]].forEach(([label,value])=>{const card=document.createElement('article');const name=document.createElement('span');name.textContent=label;const topic=document.createElement('strong');topic.textContent=value;card.append(name,topic);insight.appendChild(card)});
  const recommendation=document.createElement('p');recommendation.className='teacher-recommendation';recommendation.textContent=teacherOverallAction(data);
  const diagnostic=data.diagnostic_summary,dl=diagnosticLabels[language.value]||diagnosticLabels.English;const diagnosticPanel=document.createElement('section');diagnosticPanel.className='teacher-weekly';const diagnosticTitle=document.createElement('h4');diagnosticTitle.textContent=dl.title;const diagnosticStats=document.createElement('div');diagnosticStats.className='teacher-weekly-stats';[[dl.completed,diagnostic.completed],[dl.learners,diagnostic.learners],[dl.average,`${diagnostic.average_percentage}%`],[dl.focus,diagnostic.common_focus_topic||dcopy('noData')]].forEach(([label,value])=>{const card=document.createElement('article');const name=document.createElement('span');name.textContent=label;const detail=document.createElement('strong');detail.textContent=value;card.append(name,detail);diagnosticStats.appendChild(card)});diagnosticPanel.append(diagnosticTitle,diagnosticStats);
  const week=data.weekly_summary;const weekly=document.createElement('section');weekly.className='teacher-weekly';const weeklyTitle=document.createElement('h4');weeklyTitle.textContent=dcopy('week');const weeklyStats=document.createElement('div');weeklyStats.className='teacher-weekly-stats';
  const change=week.change_points===null?dcopy('noCompare'):week.change_points>0?`+${week.change_points}`:week.change_points<0?`-${Math.abs(week.change_points)}`:dcopy('noChange');
  [[dcopy('sessions'),week.sessions],[dcopy('questions'),week.questions],[dcopy('score'),week.percentage===null?'—':`${week.percentage}%`],[dcopy('trend'),change],[dcopy('strongest'),week.strongest_topic||dcopy('noData')],[dcopy('attention'),week.weakest_topic||dcopy('noData')]].forEach(([label,value])=>{const card=document.createElement('article');const name=document.createElement('span');name.textContent=label;const detail=document.createElement('strong');detail.textContent=value;card.append(name,detail);weeklyStats.appendChild(card)});const weeklyAction=document.createElement('p');weeklyAction.textContent=teacherAction(data);weekly.append(weeklyTitle,weeklyStats,weeklyAction);
  const trend=document.createElement('section');trend.className='teacher-trend';const trendTitle=document.createElement('h4');trendTitle.textContent=dcopy('sixWeek');const bars=document.createElement('div');bars.className='teacher-trend-bars';
  data.weekly_trend.forEach(item=>{const column=document.createElement('div');const value=document.createElement('strong');value.textContent=item.percentage===null?'—':`${item.percentage}%`;const bar=document.createElement('i');bar.style.height=`${Math.max(item.percentage||0,4)}%`;bar.title=`${item.sessions} sessions · ${item.questions} questions`;const label=document.createElement('span');label.textContent=new Date(`${item.week_start}T00:00:00`).toLocaleDateString(undefined,{day:'numeric',month:'short'});column.append(value,bar,label);bars.appendChild(column)});trend.append(trendTitle,bars);
  const note=document.createElement('p');note.className='teacher-privacy-note';note.textContent=`${data.class_level} aggregate only. No learner names or identifiers are displayed.`;
  const topics=document.createElement('section');topics.className='topic-progress';const topicTitle=document.createElement('h4');topicTitle.textContent=dcopy('topicPerformance');topics.appendChild(topicTitle);data.topics.forEach(item=>{const row=document.createElement('article');row.textContent=`${item.topic}: ${item.percentage}% · ${item.questions} ${dcopy('questions').toLowerCase()}`;topics.appendChild(row)});teacherDashboardContent.append(stats,diagnosticPanel,weekly,insight,recommendation,trend,note,topics);
}

async function refreshTeacherDashboard(){
  if(!teacherDashboardAccessKey)return;teacherDashboardContent.textContent=`Loading ${teacherClass.value} performance…`;learnerIdentity.textContent=`TEACHER DASHBOARD · ${teacherClass.value}`;
  try{showTeacherDashboard(await fetchTeacherDashboard(teacherDashboardAccessKey))}catch(error){teacherDashboardContent.textContent=error.message}
}

function downloadTeacherDashboardReport(){
  if(!currentTeacherDashboard)return;const data=currentTeacherDashboard;const week=data.weekly_summary;const diagnostic=data.diagnostic_summary;const rows=[['Robo-Teacher Privacy-Safe Class Report'],['Class',data.class_level],['Generated',new Date().toISOString()],[],['Diagnostic placement'],['Completed tests',diagnostic.completed],['Learners assessed',diagnostic.learners],['Average',`${diagnostic.average_percentage}%`],['Most common starting topic',diagnostic.common_focus_topic||'Not enough data'],[],['Learners',data.learners],['Sessions',data.sessions],['Questions',data.questions],['Average',`${data.average_percentage}%`],['Strongest topic',data.strongest_topic||'Not enough data'],['Weakest topic',data.weakest_topic||'Not enough data'],['Recommendation',data.recommendation],[],['This week'],['Week starting',week.week_start],['Sessions',week.sessions],['Questions',week.questions],['Score',week.percentage===null?'':`${week.percentage}%`],['Change in percentage points',week.change_points??''],['Strongest topic',week.strongest_topic||'Not enough data'],['Weakest topic',week.weakest_topic||'Not enough data'],['Teacher action',week.action],[],['Topic','Sessions','Questions','Percentage'],...data.topics.map(item=>[item.topic,item.sessions,item.questions,`${item.percentage}%`]),[],['Week starting','Sessions','Questions','Percentage'],...data.weekly_trend.map(item=>[item.week_start,item.sessions,item.questions,item.percentage===null?'':`${item.percentage}%`])];
  const csv=rows.map(row=>row.map(value=>`"${String(value??'').replaceAll('"','""')}"`).join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download=`robo-teacher-${data.class_level.toLowerCase()}-class-report.csv`;link.click();URL.revokeObjectURL(url)
}

function qaStorage(){try{return JSON.parse(localStorage.getItem('roboTeacherQaChecklist')||'{}')}catch(_error){return {}}}
function showQaChecklist(){teacherDashboard.classList.add('hidden');qaChecklist.classList.remove('hidden');renderQaChecklist()}
function renderQaChecklist(){
  const saved=qaStorage();qaChecklistItems.replaceChildren();let total=0,completed=0,passed=0,blockers=0;
  Object.entries(qaChecks).forEach(([group,checks])=>{const section=document.createElement('section');section.className='qa-group';const heading=document.createElement('h4');heading.textContent=group;section.appendChild(heading);checks.forEach(check=>{total+=1;const key=`${group}:${check}`,record=saved[key]||{};if(record.status&&record.status!=='Not tested')completed+=1;if(record.status==='Pass')passed+=1;if(record.status==='Fail')blockers+=1;const row=document.createElement('div');row.className='qa-item';const label=document.createElement('label');label.textContent=check;const select=document.createElement('select');['Not tested','Pass','Fail','Needs improvement'].forEach(value=>{const option=document.createElement('option');option.value=value;option.textContent=value;select.appendChild(option)});select.value=record.status||'Not tested';const note=document.createElement('input');note.placeholder='Optional test note';note.value=record.note||'';const save=()=>{const latest=qaStorage();latest[key]={status:select.value,note:note.value.trim(),updated:new Date().toISOString()};localStorage.setItem('roboTeacherQaChecklist',JSON.stringify(latest));renderQaChecklist()};select.addEventListener('change',save);note.addEventListener('change',save);row.append(label,select,note);section.appendChild(row)});qaChecklistItems.appendChild(section)});
  qaCompleted.textContent=`${completed}/${total}`;qaPassed.textContent=passed;qaBlockers.textContent=blockers;qaReleaseStatus.textContent=blockers?'Production release is blocked until every failed check is corrected.':completed===total?'All checks are complete with no release blockers. PR #9 can move to final approval.':'Complete every check before approving PR #9 for production.';
}
function downloadQaChecklistReport(){const saved=qaStorage();const rows=[['Robo-Teacher V2.5 Staging QA Report'],['Generated',new Date().toISOString()],[],['Test group','Check','Status','Note','Last updated']];Object.entries(qaChecks).forEach(([group,checks])=>checks.forEach(check=>{const record=saved[`${group}:${check}`]||{};rows.push([group,check,record.status||'Not tested',record.note||'',record.updated||''])}));const csv=rows.map(row=>row.map(value=>`"${String(value).replaceAll('"','""')}"`).join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download=`robo-teacher-v25-qa-${new Date().toISOString().slice(0,10)}.csv`;link.click();URL.revokeObjectURL(url)}

function renderProgress(data){
  progressLoading.classList.add('hidden');progressLoading.classList.remove('error');setLearningStatus('Progress ready');
  if(!data.sessions&&!data.latest_diagnostic){progressEmpty.classList.remove('hidden');return}
  progressEmpty.classList.add('hidden');
  progressDashboard.classList.remove('hidden');progressSessions.textContent=data.sessions;progressQuestions.textContent=data.total_questions;
  progressAverage.textContent=`${data.average_percentage}%`;progressStrongest.textContent=data.strongest_topic||'—';progressRecommendation.textContent=learnerRecommendation(data);document.querySelectorAll('[data-progress-label]').forEach(item=>{item.textContent=dcopy(item.dataset.progressLabel)});practiceRecommendation.textContent=dcopy('continue');
  const week=data.weekly_summary;weeklySessions.textContent=`${week.sessions} ${dcopy('sessions').toLowerCase()}`;weeklyQuestions.textContent=`${week.questions} ${dcopy('questions').toLowerCase()}`;weeklyScore.textContent=`${week.percentage}%`;
  weeklyImprovement.textContent=weeklyImprovementText(week);
  weeklyStrongest.textContent=week.strongest_topic||'—';weeklyFocus.textContent=week.focus_topic||'—';weeklyNextAction.textContent=weeklyAction(week);
  progressStorageNotice.classList.toggle('hidden',data.storage_synced);progressTopics.replaceChildren();recentSessions.replaceChildren();renderLearningPath(data.learning_path||[]);
  data.topics.forEach(item=>{
    const row=document.createElement('article');const label=document.createElement('div');const name=document.createElement('strong');const score=document.createElement('span');
    name.textContent=item.topic;score.textContent=`${item.percentage}% · ${item.correct}/${item.attempted}`;label.append(name,score);
    const track=document.createElement('div');track.className='progress-track';const fill=document.createElement('i');fill.style.width=`${item.percentage}%`;track.appendChild(fill);row.append(label,track);progressTopics.appendChild(row);
  });
  data.recent_sessions.forEach(item=>{
    const row=document.createElement('article');const detail=document.createElement('div');const topic=document.createElement('strong');const meta=document.createElement('span');const score=document.createElement('b');
    topic.textContent=item.topic;meta.textContent=`${item.difficulty} · ${formatProgressDate(item.timestamp)}`;score.textContent=`${item.percentage}%`;detail.append(topic,meta);row.append(detail,score);recentSessions.appendChild(row);
  });
}

function formatProgressDate(value){
  const date=new Date(value);return Number.isNaN(date.getTime())?'Completed':date.toLocaleDateString(undefined,{day:'numeric',month:'short'});
}

function closeProgress(){
  progressArea.classList.add('hidden');if(canvasAnswer.textContent.trim())canvasWork.classList.remove('hidden');else canvasEmpty.classList.remove('hidden');setActiveMode(chatButton);setLearningStatus('Ready to learn');
}

function openPracticeFromProgress(){resetPracticeSetup();openPractice()}

function openRecommendedPractice(){
  resetPracticeSetup();practiceClass.value=learnerClass.value;updatePracticeTopics();
  if(currentProgress&&classTopics[learnerClass.value].includes(currentProgress.recommended_topic)){
    const selectedTerm=currentProgress.recommended_term||Object.entries(practiceCurriculum[learnerClass.value]).find(([,topics])=>topics.includes(currentProgress.recommended_topic))?.[0];
    if(selectedTerm){practiceTerm.value=selectedTerm;updatePracticeTopics();practiceTopic.value=currentProgress.recommended_topic}practiceDifficulty.value='Auto'
  }
  openPractice();
}

function openLearningPathTopic(term,topic){
  resetPracticeSetup();practiceClass.value=learnerClass.value;practiceTerm.value=term;updatePracticeTopics();practiceTopic.value=topic;
  practiceDifficulty.value='Auto';openPractice();
}

function renderLearningPath(terms){
  learningPath.replaceChildren();const labels=pathCopy[language.value]||pathCopy.English;
  terms.forEach(term=>{const section=document.createElement('section');const heading=document.createElement('h5');heading.textContent=term.term;const topics=document.createElement('div');topics.className='learning-path-topics';
    term.topics.forEach(item=>{const card=document.createElement('article');card.className=`learning-path-topic ${item.status.replace('_','-')}`;const copy=document.createElement('div');const name=document.createElement('strong');name.textContent=item.topic;const detail=document.createElement('span');detail.textContent=item.percentage===null?labels[item.status]:`${labels[item.status]} · ${item.percentage}%`;copy.append(name,detail);const button=document.createElement('button');button.type='button';button.dataset.term=term.term;button.dataset.topic=item.topic;button.textContent=item.status==='recommended'?labels.continue:item.status==='not_started'?labels.start:labels.practise;button.setAttribute('aria-label',`${button.textContent.replace(' →','')} ${item.topic}`);card.append(copy,button);topics.appendChild(card)});
    section.append(heading,topics);learningPath.appendChild(section)});
}

function clearWhiteboard(){
  boardContext.save();boardContext.fillStyle='#ffffff';boardContext.fillRect(0,0,whiteboard.width,whiteboard.height);boardContext.restore();
  boardHasInk=false;
}

function openWhiteboard(){
  dismissLessonOverlays();restoreTeacherPanel();
  canvasEmpty.classList.add('hidden');canvasWork.classList.add('hidden');practiceArea.classList.add('hidden');progressArea.classList.add('hidden');whiteboardArea.classList.remove('hidden');setActiveMode(whiteboardButton);setLearningStatus('Whiteboard ready');
  if(!whiteboard.dataset.ready){clearWhiteboard();whiteboard.dataset.ready='true'}
}

function closeWhiteboard(){
  whiteboardArea.classList.add('hidden');
  if(canvasAnswer.textContent.trim())canvasWork.classList.remove('hidden');else canvasEmpty.classList.remove('hidden');setActiveMode(chatButton);setLearningStatus('Ready to learn');
}

function selectDrawingTool(tool){
  drawingTool=tool;penTool.classList.toggle('active',tool==='pen');eraserTool.classList.toggle('active',tool==='eraser');
}

function boardPoint(event){
  const rect=whiteboard.getBoundingClientRect();
  return {x:(event.clientX-rect.left)*whiteboard.width/rect.width,y:(event.clientY-rect.top)*whiteboard.height/rect.height};
}

function startDrawing(event){
  drawing=true;whiteboard.setPointerCapture(event.pointerId);const point=boardPoint(event);
  boardContext.beginPath();boardContext.moveTo(point.x,point.y);event.preventDefault();
}

function drawOnWhiteboard(event){
  if(!drawing)return;const point=boardPoint(event);
  boardContext.lineCap='round';boardContext.lineJoin='round';
  boardContext.strokeStyle=drawingTool==='eraser'?'#ffffff':'#10203a';
  boardContext.lineWidth=drawingTool==='eraser'?34:6;
  boardContext.lineTo(point.x,point.y);boardContext.stroke();event.preventDefault();
  if(drawingTool==='pen')boardHasInk=true;
}

function stopDrawing(event){
  if(!drawing)return;drawOnWhiteboard(event);drawing=false;boardContext.closePath();
}

async function submitWhiteboard(){
  if(!boardHasInk){addMessage('Please write a Maths problem or show some working on the whiteboard first.','teacher');return;}
  // This runs inside the learner's tap. Keep the audio session active while
  // the server reads the board so mobile browsers permit automatic playback.
  stopTeacherAudio();
  try{await startAudioKeepAlive()}catch(_error){/* The written answer still works without audio. */}
  submitBoardButton.disabled=true;submitBoardButton.textContent='Preparing…';
  const imageData=whiteboard.toDataURL('image/png');
  problemPreview.src=imageData;canvasWork.classList.remove('text-only');problemPreview.hidden=false;
  backToWhiteboard.classList.remove('hidden');whiteboardArea.classList.add('hidden');
  canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');
  canvasStatus.textContent='Robo-Teacher is reading your whiteboard…';canvasAnswer.textContent='';
  const thinking=addMessage('I’m reading the Maths work on your whiteboard…','teacher');
  try{
    const token=await ensureSession();
    const response=await fetch('/api/classroom/whiteboard',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({session_token:token,image_data:imageData,caption:question.value.trim(),language:language.value})});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session');}
    if(!response.ok)throw new Error(data.detail||'request');
    showCanvasAnswer(data.reply,'Whiteboard solution ready',true);
    void speakText(data.reply,true);
    thinking.textContent='I’ve placed the complete whiteboard explanation on the Teaching Canvas.';question.value='';
  }catch(err){
    stopTeacherAudio();
    const detail=err.message||'';
    thinking.textContent=detail&&!['request','session','Failed to fetch'].includes(detail)?detail:'I could not send that whiteboard. Please return to it and try again.';
    canvasStatus.textContent='Whiteboard needs attention';
  }finally{submitBoardButton.disabled=false;submitBoardButton.textContent='Ask Teacher →';}
}

function setRecordingState(recording){
  micButton.classList.toggle('recording',recording);
  micButton.textContent=recording?'Stop':'Voice';setLearningStatus(recording?'Listening':'Preparing your answer',recording?'listening':'thinking');
  micButton.setAttribute('aria-label',recording?'Stop voice question':'Start voice question');
}

async function toggleRecording(){
  if(mediaRecorder&&mediaRecorder.state==='recording'){mediaRecorder.stop();return;}
  if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){
    addMessage('Voice recording is not supported in this browser. Please type your question instead.','teacher');return;
  }
  try{
    if(currentLesson)pauseLessonForQuestion('voice');
    // A learner starting a new question always interrupts the current answer.
    stopTeacherAudio();
    // Unlock audio during the learner's click so the later automatic spoken
    // answer is not blocked after transcription and tutoring have completed.
    await startAudioKeepAlive();
    await ensureSession();
    micStream=await navigator.mediaDevices.getUserMedia({audio:true});recordedChunks=[];
    const preferred=['audio/webm;codecs=opus','audio/webm','audio/ogg;codecs=opus'];
    const mimeType=preferred.find(type=>MediaRecorder.isTypeSupported(type));
    mediaRecorder=mimeType?new MediaRecorder(micStream,{mimeType}):new MediaRecorder(micStream);
    mediaRecorder.addEventListener('dataavailable',event=>{if(event.data.size)recordedChunks.push(event.data)});
    mediaRecorder.addEventListener('stop',finishRecording,{once:true});
    mediaRecorder.start();setRecordingState(true);
    addMessage('Listening… Tap Stop when you finish your Maths question.','teacher');
  }catch(_){
    stopTeacherAudio();stopMicTracks();setRecordingState(false);
    addMessage('I could not access the microphone. Please allow microphone access or type your question.','teacher');
  }
}

function stopMicTracks(){if(micStream){micStream.getTracks().forEach(track=>track.stop());micStream=null}}

async function finishRecording(){
  setRecordingState(false);stopMicTracks();
  const type=(mediaRecorder?.mimeType||recordedChunks[0]?.type||'audio/webm').split(';',1)[0];
  const blob=new Blob(recordedChunks,{type});mediaRecorder=null;recordedChunks=[];
  if(!blob.size){stopTeacherAudio();addMessage('I did not receive any audio. Please try recording again.','teacher');return;}
  if(blob.size>12*1024*1024){stopTeacherAudio();addMessage('That recording is too large. Please keep it shorter and try again.','teacher');return;}
  const thinking=addMessage('I’m listening carefully to your Maths question…','teacher');
  micButton.disabled=true;
  try{
    const token=await ensureSession();const body=new FormData();body.append('session_token',token);body.append('language',language.value);
    body.append('audio',blob,`maths-question.${type.includes('ogg')?'ogg':'webm'}`);
    const response=await fetch('/api/classroom/audio',{method:'POST',headers:{'Accept':'application/json'},body});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session');}
    if(!response.ok)throw new Error(data.detail||'request');
    if(lessonInterruption){lessonHistory.push(lessonInterruption);lessonInterruption=null;lessonDirector.classList.remove('lesson-paused')}
    canvasWork.classList.add('text-only');problemPreview.hidden=true;
    backToWhiteboard.classList.add('hidden');
    showCanvasAnswer(data.reply,'Voice question explained',true);
    // Start reading as soon as the written voice answer reaches the canvas.
    void speakText(data.reply,true,true);
    thinking.textContent='I’ve placed the complete answer to your voice question on the Teaching Canvas.';
  }catch(err){
    stopTeacherAudio();
    const detail=err.message||'';
    thinking.textContent=detail&&!['request','session','Failed to fetch'].includes(detail)?detail:'I could not process that recording. Please try again or type your question.';
  }finally{micButton.disabled=false;}
}

async function simplifyCurrentAnswer(){
  const currentAnswer=canvasAnswer.textContent.trim();
  if(!currentAnswer){addMessage('Ask a Maths question first, then I can explain the answer more simply.','teacher');return;}
  stopTeacherAudio();
  try{await startAudioKeepAlive()}catch(_error){/* The simpler written answer still works without audio. */}
  simplifyButton.disabled=true;simplifyButton.textContent='Simplifying…';
  setLearningStatus('Preparing a simpler explanation','thinking');
  const thinking=addMessage('I’m rewriting that explanation in a simpler way…','teacher');
  try{
    const token=await ensureSession();
    const response=await fetch('/api/classroom/simplify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:currentAnswer,session_token:token,language:language.value})});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session')}
    if(!response.ok)throw new Error(data.detail||'simplify');
    recordLearningSignal('simplifications');showCanvasAnswer(data.explanation,'Simpler explanation',true);
    void speakText(data.explanation,true);
    thinking.textContent='I’ve simplified the explanation and added a familiar example.';
  }catch(error){
    stopTeacherAudio();
    thinking.textContent=error.message&&!['simplify','session'].includes(error.message)?error.message:'I could not simplify that explanation right now. Please try again.';
    setLearningStatus('Simpler explanation needs another try','attention');
  }finally{simplifyButton.disabled=false;simplifyButton.textContent='Explain Simpler';}
}

async function startUnderstandingCheck(){
  const currentAnswer=canvasAnswer.textContent.trim();
  if(!currentAnswer){addMessage('Ask a Maths question first, then I can check your understanding.','teacher');return;}
  stopTeacherAudio();understandingButton.disabled=true;understandingButton.textContent='Preparing…';
  setLearningStatus('Preparing one understanding question','thinking');
  try{
    const token=await ensureSession();
    const response=await fetch('/api/classroom/understanding/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:currentAnswer,session_token:token,language:language.value})});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session')}
    if(!response.ok)throw new Error(data.detail||'understanding');
    dismissLessonOverlays();understandingCheckId=data.check_id;understandingQuestion.textContent=data.question;understandingChoices.replaceChildren();
    data.choices.forEach((choice,index)=>{
      const label=document.createElement('label');const input=document.createElement('input');const span=document.createElement('span');
      input.type='radio';input.name='understandingChoice';input.value=String(index);input.required=true;span.textContent=choice;label.append(input,span);understandingChoices.appendChild(label);
    });
    understandingFeedback.className='practice-feedback hidden';understandingFeedback.textContent='';
    canvasWork.classList.add('hidden');canvasEmpty.classList.add('hidden');understandingArea.classList.remove('hidden');enterTeachingStage('check');
    setLearningStatus('Choose the best answer');
  }catch(error){
    addMessage(error.message&&!['understanding','session'].includes(error.message)?error.message:'I could not prepare the question right now. Please try again.','teacher');
    setLearningStatus('Understanding check needs another try','attention');
  }finally{understandingButton.disabled=false;understandingButton.textContent='Check Understanding';}
}

async function submitUnderstandingAnswer(event){
  event.preventDefault();const selected=understandingForm.querySelector('input[name="understandingChoice"]:checked');
  if(!selected||!understandingCheckId)return;
  const submitButton=understandingForm.querySelector('button[type="submit"]');submitButton.disabled=true;submitButton.textContent='Checking…';
  try{
    const token=await ensureSession();
    const response=await fetch('/api/classroom/understanding/answer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_token:token,check_id:understandingCheckId,choice_index:Number(selected.value)})});
    const data=await response.json();if(!response.ok)throw new Error(data.detail||'answer');
    recordLearningSignal(data.correct?'correct':'incorrect');
    understandingChoices.querySelectorAll('label').forEach((label,index)=>{label.classList.toggle('correct-choice',index===data.correct_index);label.querySelector('input').disabled=true});
    understandingFeedback.textContent=`${data.correct?'Correct!':'Not quite.'} ${data.feedback}`;
    understandingFeedback.className=`practice-feedback ${data.correct?'correct':'incorrect'}`;
    setLearningStatus(data.correct?'You understood it':'Review the explanation and try another check',data.correct?'success':'attention');
    submitButton.textContent=data.correct?'Correct':'Checked';
  }catch(error){understandingFeedback.textContent=error.message||'I could not check that answer. Please try again.';understandingFeedback.className='practice-feedback incorrect';submitButton.disabled=false;submitButton.textContent='Check my answer';}
}

function closeUnderstandingCheck(){
  understandingArea.classList.add('hidden');understandingCheckId=null;
  restoreTeachingStage();
}

async function showVisualExplanation(){
  const lesson=canvasAnswer.textContent.trim();if(!lesson){addMessage('Ask a Maths question first, then I can show a visual explanation.','teacher');return;}
  stopTeacherAudio();visualButton.disabled=true;visualButton.textContent='Preparing…';setLearningStatus('Drawing a lesson visual','thinking');
  try{
    const token=await ensureSession();let response;let data;
    for(let attempt=1;attempt<=3;attempt++){
      response=await fetch('/api/classroom/visual',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:lesson,session_token:token,language:language.value})});data=await response.json();
      if(response.ok)break;
      if(![429,503].includes(response.status)||attempt===3)throw new Error(data.detail||'visual');
      setLearningStatus(`Visual busy — retrying (${attempt}/2)`,'thinking');
      await new Promise(resolve=>setTimeout(resolve,attempt*450));
    }
    if(!response.ok)throw new Error(data.detail||'visual');dismissLessonOverlays();renderVisualAid(data);canvasWork.classList.add('hidden');canvasEmpty.classList.add('hidden');visualArea.classList.remove('hidden');
    enterTeachingStage('visual');setLearningStatus('Visual explanation ready','success');
  }catch(error){addMessage(error.message&&!['visual'].includes(error.message)?error.message:'I could not prepare the visual right now. Please try again.','teacher');setLearningStatus('Visual needs another try','attention');}
  finally{visualButton.disabled=false;visualButton.textContent='Show Visual';}
}

function renderVisualAid(data){
  visualTitle.textContent=data.title;visualCaption.textContent=data.caption;visualGraphic.replaceChildren();visualGraphic.dataset.kind=data.kind;
  if(data.kind==='square_grid'){const total=Math.round(data.items[0].value),side=Math.round(Math.sqrt(total)),grid=document.createElement('div');grid.className='square-grid';grid.style.setProperty('--grid-side',String(side));for(let index=0;index<total;index++){const cell=document.createElement('span');cell.setAttribute('aria-hidden','true');grid.appendChild(cell)}const label=document.createElement('strong');label.textContent=`${side} × ${side} = ${total}`;visualGraphic.append(grid,label);return;}
  if(data.kind==='fraction'){const numerator=Math.round(data.items[0].value),denominator=Math.round(data.items[1].value),model=document.createElement('div');model.className='fraction-model';model.style.setProperty('--fraction-parts',String(denominator));for(let index=0;index<denominator;index++){const part=document.createElement('span');if(index<numerator)part.className='shaded';model.appendChild(part)}const label=document.createElement('strong');label.textContent=`${numerator}/${denominator}`;visualGraphic.append(model,label);return;}
  if(data.kind==='balance'){const beam=document.createElement('div');beam.className='balance-model';data.items.slice(0,2).forEach(item=>{const side=document.createElement('div'),value=document.createElement('strong'),label=document.createElement('span');value.textContent=String(item.value);label.textContent=item.label;side.append(value,label);beam.appendChild(side)});visualGraphic.appendChild(beam);return;}
  if(data.kind==='coordinate'){const graph=document.createElement('div');graph.className='coordinate-model';data.items.forEach(item=>{const match=item.label.match(/^\s*\(?\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)?\s*$/);if(!match)return;const x=Number(match[1]),y=Number(match[2]),point=document.createElement('span');point.style.left=`${Math.max(0,Math.min(100,50+x*8))}%`;point.style.bottom=`${Math.max(0,Math.min(100,50+y*8))}%`;point.title=`(${x}, ${y})`;point.setAttribute('aria-label',point.title);graph.appendChild(point)});visualGraphic.appendChild(graph);return;}
  const max=Math.max(...data.items.map(item=>Math.abs(item.value)),1);
  data.items.forEach((item,index)=>{const node=document.createElement('div');node.className='visual-item';const mark=document.createElement('strong');const label=document.createElement('span');label.textContent=item.label;if(data.kind==='steps')mark.textContent=String(index+1);else if(data.kind==='bars'){mark.style.width=`${Math.max(12,Math.abs(item.value)/max*100)}%`;mark.textContent=String(item.value)}else mark.textContent=String(item.value);node.append(mark,label);visualGraphic.appendChild(node);});
}

function restoreTeacherPanel(){teacherPanel.classList.remove('minimized');classroom.classList.remove('teacher-min');toggle.textContent='Hide';toggle.setAttribute('aria-expanded','true')}

function stopLessonMedia(){if(mediaReplayTimer){clearInterval(mediaReplayTimer);mediaReplayTimer=null}mediaFrame.removeAttribute('src');mediaArea.classList.add('hidden')}

function dismissLessonOverlays(){stopLessonMedia();visualArea.classList.add('hidden');understandingArea.classList.add('hidden')}

function closeVisualExplanation(){visualArea.classList.add('hidden');restoreTeachingStage()}

async function openLessonMedia(){
  const lesson=Array.from(canvasAnswer.querySelectorAll('p')).map(item=>item.innerText.trim()).filter(Boolean).join('\n')||canvasAnswer.innerText.trim();if(!lesson){addMessage('Ask a Maths question first, then I can show an example.','teacher');return;}
  stopTeacherAudio();mediaButton.disabled=true;mediaButton.textContent='Preparing…';setLearningStatus('Preparing a learning example','thinking');
  try{const token=await ensureSession();const response=await fetch('/api/classroom/media',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:lesson,session_token:token,language:language.value})});const data=await response.json();if(!response.ok)throw new Error(data.detail||'media');dismissLessonOverlays();renderLessonMedia(data);canvasWork.classList.add('hidden');canvasEmpty.classList.add('hidden');mediaArea.classList.remove('hidden');enterTeachingStage('example');setLearningStatus('Learning example ready','success');}
  catch(error){addMessage(error.message||'I could not prepare that example. Please try again.','teacher');setLearningStatus('Example needs another try','attention');}
  finally{mediaButton.disabled=false;mediaButton.textContent='Watch or Explore';}
}

function renderLessonMedia(data){
  if(mediaReplayTimer){clearInterval(mediaReplayTimer);mediaReplayTimer=null}mediaTitle.textContent=data.title;mediaSource.textContent=`Source: ${data.source}`;mediaFrame.classList.add('hidden');mediaReplay.classList.add('hidden');mediaFrame.removeAttribute('src');mediaReplay.replaceChildren();
  closeMediaButton.textContent=data.kind==='simulation'?'← Exit simulation':'← Exit example';if(data.kind==='simulation'){mediaFrame.src=data.url;mediaFrame.classList.remove('hidden');return;}
  mediaReplay.classList.remove('hidden');const steps=data.steps.map((text,index)=>{const item=document.createElement('p');item.textContent=`${index+1}. ${text}`;mediaReplay.appendChild(item);return item});let active=0;const show=()=>steps.forEach((item,index)=>item.classList.toggle('active',index===active));show();mediaReplayTimer=setInterval(()=>{active=(active+1)%steps.length;show()},2600);
}

function closeLessonMedia(){stopLessonMedia();restoreTeachingStage()}

async function handleImage(file,source='upload'){
  if(!file)return;
  if(!['image/jpeg','image/png','image/webp'].includes(file.type)){
    addMessage('Please choose a JPEG, PNG, or WebP image.','teacher');return;
  }
  if(file.size>8*1024*1024){addMessage('Please choose an image no larger than 8 MB.','teacher');return;}
  if(previewUrl)URL.revokeObjectURL(previewUrl);
  previewUrl=URL.createObjectURL(file);problemPreview.src=previewUrl;
  canvasWork.classList.remove('text-only');problemPreview.hidden=false;
  backToWhiteboard.classList.toggle('hidden',source!=='whiteboard');
  whiteboardArea.classList.add('hidden');
  canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');
  canvasStatus.textContent='Robo-Teacher is reading your image…';canvasAnswer.textContent='';setLearningStatus('Reading your image','thinking');
  const thinking=addMessage('I’m reading the Maths problem in your image…','teacher');
  uploadButton.disabled=true;cameraButton.disabled=true;
  try{
    const token=await ensureSession();
    const body=new FormData();body.append('session_token',token);body.append('language',language.value);body.append('image',file);
    const caption=question.value.trim();if(caption)body.append('caption',caption);
    const response=await fetch('/api/classroom/image',{method:'POST',headers:{'Accept':'application/json'},body});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session');}
    if(!response.ok)throw new Error(data.detail||'request');
    showCanvasAnswer(data.reply,'Teaching response ready');
    thinking.textContent='I’ve placed the complete image explanation on the Teaching Canvas.';
    question.value='';
  }catch(err){
    const message=err.message&&!['request','session','Failed to fetch'].includes(err.message)?err.message:'I could not read that image. Please try a clearer photo.';
    thinking.textContent=message;canvasStatus.textContent='Image needs attention';
  }finally{uploadButton.disabled=false;cameraButton.disabled=false;imageUpload.value='';cameraCapture.value='';}
}

form.addEventListener('submit',async(e)=>{
  e.preventDefault();const text=question.value.trim();if(!text||sendButton.disabled)return;
  const interruptedLesson=lessonInterruption||(currentLesson?{text:currentLesson.text,index:currentLesson.index}:null);
  const lessonQuestion=interruptedLesson?`The learner paused this lesson step: "${currentLesson.steps[currentLesson.index]}"\n\nTheir question is: ${text}`:text;
  const requestText=`${adaptivePromptContext()}\n\n${lessonQuestion}`;
  addMessage(text,'student');question.value='';sendButton.disabled=true;sendButton.textContent='Thinking…';setLearningStatus('Working through your question','thinking');
  const thinking=addMessage('Let me work through that with you…','teacher');
  try{
    const token=await ensureSession();
    const response=await fetch('/api/classroom/chat',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({message:requestText,session_token:token,language:language.value})});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session');}
    if(!response.ok)throw new Error(data.detail||'request');
    if(interruptedLesson){lessonHistory.push(interruptedLesson);lessonInterruption=null;lessonDirector.classList.remove('lesson-paused')}
    canvasWork.classList.add('text-only');problemPreview.hidden=true;
    backToWhiteboard.classList.add('hidden');
    showCanvasAnswer(data.reply,'Worked solution');
    if(handsFree.enabled)void speakText(data.reply,true,true);
    thinking.textContent='I’ve placed the complete worked solution on the Teaching Canvas.';
  }catch(err){
    thinking.textContent=err.message&&err.message.includes('wait')?err.message:'Sorry, I had a small technical hiccup. Please try your question again in a moment.';
  }finally{sendButton.disabled=false;sendButton.textContent='Send';setLearningStatus('Answer ready');keepTeachingCanvasVisible();if(handsFree.enabled){handsFree.processing=false;handsFree.restartTimer=setTimeout(startHandsFreeListening,500)}}
});
