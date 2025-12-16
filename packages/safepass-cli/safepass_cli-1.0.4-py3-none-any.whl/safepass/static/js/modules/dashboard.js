/* SafePass - Dashboard Module */

document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
    animateScoreCircle();
});

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();
        
        if (response.ok) {
            updateStatsDisplay(data);
        }
    } catch (error) {
        console.error('Dashboard stats yüklenemedi:', error);
    }
}

function updateStatsDisplay(stats) {
    // Stats kartlarını güncelle
    document.querySelectorAll('.stat-value').forEach((element, index) => {
        const values = [
            stats.total_cards,
            stats.strong_count,
            stats.medium_count,
            stats.weak_count
        ];
        animateValue(element, 0, values[index] || 0, 1000);
    });
}

function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

function animateScoreCircle() {
    const scoreCircle = document.querySelector('.score-circle');
    const scoreLabel = document.querySelector('.score-label');
    
    if (scoreCircle) {
        const score = parseInt(scoreCircle.dataset.score) || 0;
        scoreCircle.style.setProperty('--score', score);
        
        // Skora göre renk sınıfı ekle
        let colorClass = 'score-poor';
        let labelText = 'Zayıf Güvenlik 🚨';
        
        if (score >= 90) {
            colorClass = 'score-excellent';
            labelText = 'Mükemmel Güvenlik 🏆';
        } else if (score >= 75) {
            colorClass = 'score-good';
            labelText = 'İyi Güvenlik ✅';
        } else if (score >= 50) {
            colorClass = 'score-medium';
            labelText = 'Orta Güvenlik ⚠️';
        }
        
        // Eski renk sınıflarını temizle
        scoreCircle.classList.remove('score-excellent', 'score-good', 'score-medium', 'score-poor');
        scoreCircle.classList.add(colorClass);
        
        if (scoreLabel) {
            scoreLabel.classList.remove('score-excellent', 'score-good', 'score-medium', 'score-poor');
            scoreLabel.classList.add(colorClass);
            scoreLabel.textContent = labelText;
        }
    }
}
