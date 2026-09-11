(() => {
  const canvas=document.getElementById('canvas');
  const canvasWork=document.getElementById('canvasWork');
  const canvasAnswer=document.getElementById('canvasAnswer');
  const lessonDirector=document.getElementById('lessonDirector');
  if(!canvas||!canvasWork||!canvasAnswer||!lessonDirector)return;
  if(document.getElementById('robo-teacher-canvas-hierarchy'))return;

  canvas.classList.add('canvas-hierarchy-p1');

  const style=document.createElement('style');
  style.id='robo-teacher-canvas-hierarchy';
  style.textContent=`
    .teaching-canvas.canvas-hierarchy-p1{
      place-items:stretch;
      align-content:start;
    }
    .canvas-hierarchy-p1 .canvas-work{
      align-items:start;
      gap:20px;
    }
    .canvas-hierarchy-p1 .canvas-work>div{
      display:flex;
      flex-direction:column;
      min-width:0;
    }
    .canvas-hierarchy-p1 .canvas-result-toolbar{
      order:0;
      justify-content:flex-start;
      gap:7px;
      margin:0 0 14px;
      padding:0 0 12px;
      border-bottom:1px solid #d9e3ef;
    }
    .canvas-hierarchy-p1 .canvas-status{
      font-size:11px;
      padding:5px 9px;
    }
    .canvas-hierarchy-p1 .teaching-stage-mode,
    .canvas-hierarchy-p1 .teaching-memory-status{
      font-size:11px;
      font-weight:700;
      color:#44546a;
      background:#f1f5fa;
      border:1px solid #d7e0eb;
      border-radius:999px;
      padding:5px 9px;
    }
    .canvas-hierarchy-p1 .auto-teach-toggle,
    .canvas-hierarchy-p1 .back-to-board{
      min-height:32px;
      padding:5px 9px;
      font-size:11px;
      border-radius:9px;
    }
    .canvas-hierarchy-p1 .canvas-answer{
      order:1;
      max-height:none;
      overflow:visible;
      font-size:17px;
      line-height:1.7;
      letter-spacing:.002em;
      padding:2px 2px 10px;
    }
    .canvas-hierarchy-p1 .canvas-answer p{
      margin:0 0 14px;
    }
    .canvas-hierarchy-p1 .canvas-answer strong{
      font-weight:850;
    }
    .canvas-hierarchy-p1 .lesson-director{
      order:2;
      margin-top:8px;
      padding-top:16px;
      border-top:2px solid #dfe8f3;
    }
    .canvas-hierarchy-p1 .lesson-progress{
      display:grid;
      gap:8px;
      margin-bottom:12px;
      padding:12px 14px;
      background:#f4f8fd;
      border:1px solid #dce6f2;
      border-radius:12px;
    }
    .canvas-hierarchy-p1 #lessonStepLabel{
      font-size:15px;
      color:#10203a;
    }
    .canvas-hierarchy-p1 .lesson-step-track{
      min-height:7px;
      border-radius:999px;
      overflow:hidden;
    }
    .canvas-hierarchy-p1 .lesson-choreography-hint,
    .canvas-hierarchy-p1 .lesson-pause-notice{
      color:#43536a;
      line-height:1.55;
    }
    .canvas-hierarchy-p1 .lesson-stage-actions{
      margin-top:10px;
      padding:10px 0;
      border-top:1px solid #e0e7f0;
      border-bottom:1px solid #e0e7f0;
    }
    .canvas-hierarchy-p1 .lesson-controls{
      margin-top:12px;
    }
    .canvas-hierarchy-p1 .lesson-controls .lesson-primary{
      background:#1677ff;
      border-color:#1677ff;
      color:#fff;
      font-weight:850;
      box-shadow:0 6px 18px #1677ff24;
    }
    .canvas-hierarchy-p1 .contextual-lesson-actions{
      margin-top:18px;
    }
    @media(max-width:700px){
      .canvas-hierarchy-p1 .canvas-result-toolbar{
        gap:5px;
      }
      .canvas-hierarchy-p1 .teaching-memory-status{
        display:none;
      }
      .canvas-hierarchy-p1 .canvas-answer{
        font-size:16px;
        line-height:1.65;
        padding-bottom:8px;
      }
      .canvas-hierarchy-p1 .lesson-progress{
        padding:10px 11px;
      }
      .canvas-hierarchy-p1 .lesson-controls{
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:7px;
      }
      .canvas-hierarchy-p1 .lesson-controls button{
        width:100%;
        min-height:44px;
        margin:0;
      }
      .canvas-hierarchy-p1 .lesson-controls .lesson-primary{
        grid-column:1/-1;
        grid-row:1;
      }
    }
  `;
  document.head.appendChild(style);
})();
