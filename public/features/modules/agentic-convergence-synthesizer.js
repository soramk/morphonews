/**
 * MorphoNews Feature: エージェンティック・コンバージェンス・シンセサイザー
 * Generated: 2026-01-30_0954
 * Description: 今日のムード『Convergence』を体現し、ページ内に分散したニュースの断片を一つの重力点に引き寄せ、統合された視覚的要約を生成します。散らばった文脈を衝突・融合させることで、情報の深層を浮き彫りにします。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #convergence-synthesizer-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 10000;
            font-family: 'Inter', sans-serif;
        }
        .convergence-trigger {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #a855f7);
            box-shadow: 0 10px 25px rgba(168, 85, 247, 0.4);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            border: none;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .convergence-trigger:hover {
            transform: scale(1.1) rotate(90deg);
        }
        #convergence-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 9999;
        }
        .insight-orb {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(168, 85, 247, 0.2) 0%, rgba(0,0,0,0) 70%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: white;
            padding: 20px;
            pointer-events: none;
            transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            opacity: 0;
        }
        .insight-orb.active {
            transform: translate(-50%, -50%) scale(1);
            opacity: 1;
        }
        .insight-content {
            font-size: 1.2rem;
            font-weight: 700;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'convergence-synthesizer-container';
    container.innerHTML = `
        <button class="convergence-trigger" title="Converge Insights">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22V12m0 0l-4 4m4-4l4 4M12 2v10m0 0l4-4m-4 4l-4-4"/></svg>
        </button>
        <div id="insight-orb" class="insight-orb"><div class="insight-content"></div></div>
        <canvas id="convergence-canvas"></canvas>
    `;
    document.body.appendChild(container);

    const canvas = document.getElementById('convergence-canvas');
    const ctx = canvas.getContext('2d');
    const orb = document.getElementById('insight-orb');
    const orbContent = orb.querySelector('.insight-content');

    let particles = [];
    let isSynthesizing = false;

    const resize = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    class Particle {
        constructor(x, y, text) {
            this.x = x;
            this.y = y;
            this.text = text;
            this.targetX = window.innerWidth / 2;
            this.targetY = window.innerHeight / 2;
            this.speed = 0.02 + Math.random() * 0.03;
            this.opacity = 1;
            this.size = 12 + Math.random() * 8;
        }
        update() {
            this.x += (this.targetX - this.x) * this.speed;
            this.y += (this.targetY - this.y) * this.speed;
            const dist = Math.sqrt(Math.pow(this.targetX - this.x, 2) + Math.pow(this.targetY - this.y, 2));
            if (dist < 50) this.opacity -= 0.05;
            return this.opacity > 0;
        }
        draw() {
            ctx.fillStyle = `rgba(168, 85, 247, ${this.opacity})`;
            ctx.font = `${this.size}px sans-serif`;
            ctx.fillText(this.text, this.x, this.y);
        }
    }

    function synthesize() {
        if (isSynthesizing) return;
        isSynthesizing = true;
        
        const elements = document.querySelectorAll('h1, h2, h3, .news-title, p');
        const sources = Array.from(elements).filter(el => el.innerText.length > 5).slice(0, 15);
        
        sources.forEach(el => {
            const rect = el.getBoundingClientRect();
            const text = el.innerText.split(' ')[0].substring(0, 10);
            particles.push(new Particle(rect.left + rect.width/2, rect.top + rect.height/2, text));
        });

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles = particles.filter(p => {
                const alive = p.update();
                if (alive) p.draw();
                return alive;
            });

            if (particles.length > 0) {
                requestAnimationFrame(animate);
            } else {
                showOrb(sources);
            }
        };
        animate();
    }

    function showOrb(sources) {
        const keyTerms = sources.map(s => s.innerText.split(' ')).flat().filter(w => w.length > 3);
        const uniqueTerms = [...new Set(keyTerms)].slice(0, 3).join(' × ');
        
        orbContent.innerText = `Convergence Points:\n${uniqueTerms || 'Core Context Identified'}`;
        orb.classList.add('active');
        
        setTimeout(() => {
            orb.classList.remove('active');
            isSynthesizing = false;
        }, 4000);
    }

    document.querySelector('.convergence-trigger').addEventListener('click', synthesize);
})();
