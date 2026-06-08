import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Home() {
  const { user } = useAuth()

  return (
    <div>
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-slate-950 to-accent/10" />
        <div className="relative max-w-6xl mx-auto px-4 py-24 md:py-32 text-center">
          <p className="text-accent text-sm font-semibold tracking-widest uppercase mb-4">
            NUTECH · Department of Artificial Intelligence
          </p>
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
            Intelligent HIV/AIDS Risk Prediction
            <span className="block text-primary-light">Powered by Machine Learning</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto mb-10">
            HIVCare AI helps you assess risk using an optimized ensemble model, personalized
            recommendations, and analytics — supporting awareness, not replacing clinical diagnosis.
          </p>
          <Link
            to={user ? '/predict' : '/register'}
            className="inline-block px-8 py-4 rounded-xl bg-primary hover:bg-primary-dark font-semibold text-lg shadow-lg shadow-primary/30"
          >
            Get Started
          </Link>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 py-20">
        <h2 className="text-2xl font-bold mb-8 text-center">Project Overview</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { title: 'Risk Assessment', desc: 'Ensemble ML model with preprocessing and SMOTE balancing.' },
            { title: 'Recommendations', desc: 'Tailored guidance for low, medium, and high risk profiles.' },
            { title: 'Analytics', desc: 'Dashboards with distribution charts, ROC, and confusion matrix.' },
          ].map((item) => (
            <div key={item.title} className="p-6 rounded-2xl bg-slate-900 border border-slate-800">
              <h3 className="font-semibold text-primary-light mb-2">{item.title}</h3>
              <p className="text-slate-400 text-sm">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
