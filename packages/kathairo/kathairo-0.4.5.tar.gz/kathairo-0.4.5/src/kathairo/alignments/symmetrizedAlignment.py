from machine.corpora import ParatextTextCorpus

from machine.tokenization import LatinWordTokenizer

from machine.translation import SymmetrizationHeuristic
from machine.translation import SymmetrizedWordAlignmentModelTrainer

from machine.translation.thot import ThotIbm1WordAlignmentModel
from machine.translation.thot import ThotWordAlignmentModelTrainer 
from machine.translation.thot import ThotWordAlignmentModelType
from machine.translation.thot import ThotSymmetrizedWordAlignmentModel


source_corpus = ParatextTextCorpus("data/VBL-PT")
target_corpus = ParatextTextCorpus("data/WEB-PT")
parallel_corpus = source_corpus.align_rows(target_corpus).tokenize(LatinWordTokenizer())

src_trg_trainer = ThotWordAlignmentModelTrainer(
    ThotWordAlignmentModelType.IBM1, parallel_corpus.lowercase(), "out/VBL-WEB-IBM1/src_trg"
)
trg_src_trainer = ThotWordAlignmentModelTrainer(
    ThotWordAlignmentModelType.IBM1, parallel_corpus.invert().lowercase(), "out/VBL-WEB-IBM1/trg_src"
)
symmetrized_trainer = SymmetrizedWordAlignmentModelTrainer(src_trg_trainer, trg_src_trainer)
symmetrized_trainer.train(lambda status: print(f"{status.message}: {status.percent_completed:.2%}"))
symmetrized_trainer.save()


src_trg_model = ThotIbm1WordAlignmentModel("out/VBL-WEB-IBM1/src_trg")
trg_src_model = ThotIbm1WordAlignmentModel("out/VBL-WEB-IBM1/trg_src")
symmetrized_model = ThotSymmetrizedWordAlignmentModel(src_trg_model, trg_src_model)
symmetrized_model.heuristic = SymmetrizationHeuristic.GROW_DIAG_FINAL_AND

segment_batch = list(parallel_corpus.lowercase().take(5))
alignments = symmetrized_model.align_batch(segment_batch)

for (source_segment, target_segment), alignment in zip(segment_batch, alignments):
    print("Source:", " ".join(source_segment))
    print("Target:", " ".join(target_segment))
    print("Alignment:", alignment)