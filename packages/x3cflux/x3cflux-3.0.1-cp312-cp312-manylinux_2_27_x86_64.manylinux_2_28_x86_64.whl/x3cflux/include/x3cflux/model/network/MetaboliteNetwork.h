#ifndef X3CFLUX_METABOLITENETWORK_H
#define X3CFLUX_METABOLITENETWORK_H

#include <model/data/NetworkData.h>
#include <model/data/Substrate.h>

namespace x3cflux {

/// \brief Metabolic pool information storage
class PoolInformation {
  private:
    std::string name_;
    std::size_t numAtoms_;
    std::map<TracerElement, std::size_t> numIsotopes_;
    bool substrate_;

  public:
    /// Create metabolic pool information.
    /// \param name name of the metabolite
    /// \param numAtoms number of traceable atoms
    /// \param numIsotopes numbers of atoms from each supported isotope
    /// \param substrate indicates if substrate
    PoolInformation(std::string name, std::size_t numAtoms, std::map<TracerElement, std::size_t> numIsotopes,
                    bool substrate);

    /// \return name of the metabolite
    const std::string &getName() const;

    /// \return number of traceable atoms
    std::size_t getNumAtoms() const;

    /// \return numbers of atoms from each supported tracer element
    const std::map<TracerElement, std::size_t> &getNumIsotopes() const;

    /// \return indicates if substrate
    bool isSubstrate() const;
};

/// \brief Metabolic reaction information storage
class ReactionInformation {
  private:
    std::string name_;
    std::size_t numAtoms_;
    Permutation atomPermutation_;
    bool bidirectional_;

  public:
    /// Create metabolic reaction information.
    /// \param name name of the reaction
    /// \param numAtoms number of traceable atoms partaking
    /// \param atomPermutation permutation of the traceable atoms
    /// \param bidirectional indicates if bi- or unidirectional
    ReactionInformation(std::string name, std::size_t numAtoms, Permutation atomPermutation, bool bidirectional);

    /// \return name of the reaction
    const std::string &getName() const;

    /// \return number of traceable atoms partaking
    std::size_t getNumAtoms() const;

    /// \return permutation of the traceable atoms
    const Permutation &getAtomPermutation() const;

    /// \return indicates if bi- or unidirectional
    bool isBidirectional() const;
};

/// \brief Network of metabolite pools and reactions
///
/// The network stores the basic metabolite reaction graph needed to perform MFA.
/// It contains metabolite pools and metabolic reaction information and
/// hyperedges modeling the connections given by the reactions.
class MetaboliteNetwork {
  public:
    using Vertice = std::size_t;
    using Hyperedge = std::pair<std::vector<Vertice>, std::vector<Vertice>>;

  private:
    std::vector<PoolInformation> poolInformation_;
    std::vector<ReactionInformation> reactionInformation_;
    std::vector<Hyperedge> hyperedges_;

  public:
    /// Creates network of metabolites and reactions.
    /// \param networkData raw metabolite and reaction data
    /// \param substrates raw substrate data
    explicit MetaboliteNetwork(const NetworkData &networkData,
                               const std::vector<std::shared_ptr<Substrate>> &substrates);

    /// \param position metabolite index
    /// \return information on the metabolite
    const PoolInformation &getPoolInformation(std::size_t position) const;

    /// \param position reaction index
    /// \return information on the reaction
    const ReactionInformation &getReactionInformation(std::size_t position) const;

    /// \return number of metabolic pools
    std::size_t getNumPools() const;

    /// \return number of reactions
    std::size_t getNumReactions() const;

    /// \return number of substrates
    std::size_t getNumSubstrates() const;

    /// Reactions between metabolite pools can be modeled by hyperedges.
    /// Educts are input vertices of the reaction and products output vertices,
    /// respectively.
    /// \param reactionIndex reaction index
    /// \return hyperedge that represents the reactions connections
    const Hyperedge &getHyperedge(std::size_t reactionIndex) const;
};

} // namespace x3cflux

#endif // X3CFLUX_METABOLITENETWORK_H
