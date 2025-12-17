import React from 'react'
import '../App.css'

function AboutPage() {
  return (
    <div style={{ paddingTop: '80px' }}>
      <section className="section" style={{ background: 'white', minHeight: '100vh' }}>
        <h2 className="section-title">درباره ما</h2>
        <p className="section-subtitle">
          شناخت بیشتر از تیم و اهداف ما
        </p>
        <div className="about-content">
          <p>
            {{PROJECT_NAME}} یک شرکت پیشرو در ارائه خدمات تخصصی است که با سال‌ها تجربه
            و تیمی متشکل از متخصصان حرفه‌ای، در تلاش است تا بهترین راه‌حل‌ها را
            برای مشتریان خود فراهم کند.
          </p>
          <p>
            ما معتقدیم که کیفیت، سرعت و رضایت مشتری سه اصل اساسی در هر کسب و کاری
            است. به همین دلیل تمام تلاش خود را می‌کنیم تا با ارائه خدمات با کیفیت
            و پشتیبانی عالی، رضایت کامل شما را جلب کنیم.
          </p>
          <p>
            تیم ما متشکل از افراد با تجربه و متخصص در زمینه‌های مختلف است که
            همیشه آماده کمک و همراهی شما هستند. ما به نوآوری و استفاده از تکنولوژی‌های
            روز دنیا اعتقاد داریم و همواره در حال بهبود و به‌روزرسانی خدمات خود هستیم.
          </p>
        </div>
      </section>
    </div>
  )
}

export default AboutPage

