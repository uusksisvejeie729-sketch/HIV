export default function About() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-16">
      <h1 className="text-3xl font-bold mb-6">About HIVCare AI</h1>
      <div className="space-y-6 text-slate-300 leading-relaxed">
        <section>
          <h2 className="text-xl font-semibold text-white mb-2">Project Information</h2>
          <p>
            HIVCare AI is a full-stack healthcare support platform that predicts HIV risk using
            machine learning. Users enter health and behavioral data and receive a risk category
            with confidence scores and recommendations.
          </p>
        </section>
        <section>
          <h2 className="text-xl font-semibold text-white mb-2">Research Details</h2>
          <p>
            The system implements logistic regression, decision trees, random forest, and SVM in a
            voting ensemble. Features include BMI categories, medical risk index, and age groups.
            Evaluation targets 89%+ accuracy with precision, recall, F1, and ROC-AUC metrics.
          </p>
        </section>
        <section>
          <h2 className="text-xl font-semibold text-white mb-2">Team</h2>
          <p>
            <strong>Muhammad Umair</strong> (F24607102)<br />
            Department of Artificial Intelligence<br />
            National University of Technology (NUTECH)
          </p>
        </section>
        <p className="text-sm text-amber-400/90 border border-amber-500/30 rounded-lg p-4 bg-amber-500/5">
          Disclaimer: This tool supports healthcare awareness and decision-making. It is not a
          replacement for professional medical diagnosis or treatment.
        </p>
      </div>
    </div>
  )
}
