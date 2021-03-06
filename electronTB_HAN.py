import os.path
import time
from math import *
from math import sqrt
from numpy.linalg import *
import numpy as np
import matplotlib.pyplot as plt
import cmath
import datetime as dt
#from numeric import *


class electronTB:
    def __init__(self, dimension, num_atom, spinor):
        self.dimension = dimension
        self.num_atom = num_atom
        self.onsite_info = []
        self.hopping_info = []
        self.edge_cal = False
        if spinor:
            self.spin = 2
            print 'Not implemented yet : spinor'
            return 0
        else:
            self.spin = 1

    def set_geometry(self, lattice_vector, atom_position):
        self.latt_vec = np.array(lattice_vector)
        self.atom_pos = np.array(atom_position)
        if len(self.latt_vec) != self.dimension:
            print 'Please check either dimension or lattice vector; They are differnt to each other'
        if len(self.atom_pos) != self.num_atom:
            print 'Please check either num_atom or atom_position; They are differnt to each other'
        
        ####reciprocal lattice####

        if self.dimension == 3:
            recip_fac =  (2*np.pi) / np.dot(self.latt_vec[0], np.cross(self.latt_vec[1], self.latt_vec[2]))
            recip_vec = np.array([np.cross(self.latt_vec[1], self.latt_vec[2]), np.cross(self.latt_vec[2], self.latt_vec[0]), np.cross(self.latt_vec[0], self.latt_vec[1])]) * recip_fac
        if self.dimension == 2:
            #print np.cross(self.latt_vec[0], self.latt_vec[1])
            recip_fac =  (2*np.pi) / np.cross(self.latt_vec[0], self.latt_vec[1])
            recip_vec = np.array([[self.latt_vec[1][1],-self.latt_vec[0][1]],[-self.latt_vec[1][0],self.latt_vec[0][0]]]) * recip_fac
            recip_vec = recip_vec.transpose()
        self.recip_vec = recip_vec

        return 0

    def set_onsite(self, on_site_energy):
        if len(on_site_energy) != self.num_atom:
            print 'Please check either on_site_energy array or the number of atoms'
            return 0

        for i in range(len(on_site_energy)):
            onsite_temp = [i, i, np.zeros(self.dimension), on_site_energy[i]]
            self.onsite_info.append(onsite_temp)

        return 0

    def set_hopping(self,iatom, jatom, supercell_of_jatom, hopping_para):
        #if len(force_constant) != self.dimension or len(force_constant[0]) != self.dimension:
        #    print 'Please check either dimension or the size of force constant; They are different to each other'
        #    return 0
        if len(supercell_of_jatom) != self.dimension:
            print 'Please check either dimension or the size of supercell; They are different to each other'
            return 0
        if (iatom == jatom):
            if self.dimension == 2:
                if np.all(np.array([supercell_of_jatom]==np.array([0,0]))):
                    print 'You cannot set on-site energies by using set_hopping; use set_onsite routine'
                    return 0
            if self.dimension == 3:
                if np.all(np.array([supercell_of_jatom]==np.array([0,0,0]))):
                    print 'You cannot set on-site energies by using set_hopping; use set_onsite routine'
                    return 0

        hopping_temp = [iatom, jatom, supercell_of_jatom, hopping_para]

        #print fc_temp

        self.hopping_info.append(hopping_temp)

    def make_edge(self):
        print 'Not implemented yet'
        return 0

    def inherit_info(self, parent_class):
        if self.dimension != parent_class.dimension:
            print "ERROR: please check dimension"
            return 0
        if self.num_atom != parent_class.num_atom:
            print "ERROR: please check num_atom"
            return 0
        if self.spin != parent_class.spin:
            print "ERROR: please check spinor"
            return 0
        self.onsite_info = parent_class.onsite_info
        self.hopping_info = parent_class.hopping_info
        self.recip_vec = parent_class.recip_vec
        self.latt_vec = parent_class.latt_vec
        self.atom_pos = parent_class.atom_pos
        return 0

    def print_info(self):
        print 'Dimension = ' + str(self.dimension)
        print 'Number of atoms = ' + str(self.num_atom)
        if self.dimension == 2:
            print 'Lattice vector = ' + ' a = ' + str(self.latt_vec[0]) + ' b = ' + str(self.latt_vec[1])
        if self.dimension ==3:
            print 'Lattice vector = ' + ' a = ' + str(self.latt_vec[0]) + ' b = ' + str(self.latt_vec[1]) + ' c = ' + str(self.latt_vec[2])
        print 'Atomic position'
        for i in range(self.num_atom):
            line = ''
            for j in range(self.dimension):
                line += str(self.atom_pos[i][j]) + '\t'
            print line
        print 'On site energies'
        for i in range(len(self.onsite_info)):
            print str(self.onsite_info[i])
        print 'All hopping_info'
        for i in range(len(self.hopping_info)):
            print str(self.hopping_info[i])
        return 0

    def obtain_qpath(self, q_path, q_spacing):
        q_vec_list = []
        q_distance_list = []
        special_q_distance_list = [0.0]
        sq_distance = 0.0
        #print np.dot(recip_vec, self.latt_vec)
        for i in range(len(q_path)-1):
            initial = np.array(q_path[i])
            final = np.array(q_path[i+1])
            #print np.dot(recip_vec.transpose(), (final-initial).transpose())
            temp_sq_distance = np.linalg.norm(np.dot(self.recip_vec.transpose(), (final-initial).transpose()))
            sq_distance += temp_sq_distance
            special_q_distance_list.append(sq_distance)
            q_distance = special_q_distance_list[i]
            for j in range(q_spacing):
                delta = (final - initial) / float(q_spacing-1)
                temp = initial + delta*j
                q_vec_list.append(temp)
                temp_q_distance = np.linalg.norm(np.dot(self.recip_vec.transpose(), np.array(delta*j).transpose()))
                #print temp_q_distance
                q_distance_list.append(q_distance+temp_q_distance)

        return special_q_distance_list, q_distance_list, q_vec_list

    def find_hopping_for_pair(self, iatom, jatom):
        proper_hopping_info = []  # [r_j-r_i, hopping]
        if iatom == jatom:
            for i in range(len(self.hopping_info)):
                if (iatom == self.hopping_info[i][0] and iatom == self.hopping_info[i][1]):
                    diff_r = np.array(self.atom_pos[jatom]) + np.array(self.hopping_info[i][2]).transpose() - np.array(self.atom_pos[iatom])
                    proper_hopping_info.append([diff_r, self.hopping_info[i][3]])
            for i in range(len(self.onsite_info)):
                proper_hopping_info.append([self.onsite_info[i][2], self.onsite_info[i][3]])
        else:
            for i in range(len(self.hopping_info)):
                if (iatom == self.hopping_info[i][0] and jatom == self.hopping_info[i][1]):
                    diff_r = np.array(self.atom_pos[jatom]) + np.array(self.hopping_info[i][2]).transpose() - np.array(self.atom_pos[iatom])
                    proper_hopping_info.append([diff_r, self.hopping_info[i][3]])
                if (jatom == self.hopping_info[i][0] and iatom == self.hopping_info[i][1]):
                    diff_r = np.array(self.atom_pos[jatom])  - np.array(self.atom_pos[iatom]) -  np.array(self.hopping_info[i][2]).transpose()
                    proper_hopping_info.append([diff_r, self.hopping_info[i][3]])
        return proper_hopping_info


    def construct_H_q(self, q_vec):
        #recip_vec = self.reciprocal()
        q = np.dot(self.recip_vec.transpose(), np.array(q_vec).transpose())
        #q = np.array(q_vec)
        h = np.zeros((self.spin * self.num_atom, self.spin * self.num_atom), dtype=complex)
        for i in range(self.num_atom):
            for j in range(self.num_atom):
                if i < j:
                    proper_hopping_info = self.find_hopping_for_pair(i,j)
                    h_local = 0.0+0.0j
                    for k in range(len(proper_hopping_info)):
                        #r = np.array(proper_fc_info[k][0])
                        r = np.dot(self.latt_vec.transpose(), np.array(proper_hopping_info[k][0]).transpose())
                        #print r
                        phase_factor = np.exp(np.vdot(r, q) * 1j)
                        h_local += proper_hopping_info[k][1] * phase_factor
                    h[i, j] += h_local
                    h[j,i] += np.conjugate(h_local)
                if i  == j:
                    proper_hopping_info = self.find_hopping_for_pair(i,j)
                    h_local = 0.0+0.0j
                    for k in range(len(proper_hopping_info)):
                        #r = np.array(proper_fc_info[k][0])
                        r = np.dot(self.latt_vec.transpose(), np.array(proper_hopping_info[k][0]).transpose())
                        phase_factor = np.exp(np.vdot(r, q) * 1j)
                        if np.linalg.norm(r) == 0:
                            h_local += proper_hopping_info[k][1] * phase_factor
                        else:
                            h_local += proper_hopping_info[k][1] * phase_factor + (proper_hopping_info[k][1] * phase_factor).conj()
                    h[i, j] += h_local
        hamiltonian = (h+ h.conj().transpose()) / 2.0 

        return hamiltonian
    
    def get_electron_eigval_mesh(self, qmesh):
        if self.dimension != len(qmesh):
            print 'Check either dimension or q_point_mesh'
            return 0
        
        q_vec_list= []

        if self.dimension ==2:
            for i in range(int(qmesh[0])):
                for j in range(int(qmesh[1])):
                    qtemp = [0.0 + i*(1.0/int(qmesh[0])), 0.0 + j*(1.0/int(qmesh[1]))]
                    q_vec_list.append(qtemp)
        if self.dimension ==3:
            for i in range(int(qmesh[0])):
                for j in range(int(qmesh[1])):
                    for k in range(int(qmesh[2])):
                        qtemp = [0.0 + i*(1.0/int(qmesh[0])), 0.0 + j*(1.0/int(qmesh[1])), 0.0 + k*(1.0/int(qmesh[2]))]
                        q_vec_list.append(qtemp)

        eigval_array = []
        for i in range(self.num_atom):
            eigval_array.append([])

        for i in range(len(q_vec_list)):
            #print 'Process: ' + str(i+1) +'/' + str(len(q_vec_list))
            q_vec = q_vec_list[i]
            H = self.construct_H_q(q_vec)
            w1 = np.linalg.eigvalsh(H)
            band_num = len(w1)
            for j in range(band_num):
                eigval_array[j].append(w1[j])

        return eigval_array

    def find_filling_specific_band(self, eig_array, band_index, chemical_pot, temperatue):
        boltzman_const = 8.617343e-5 # eV/K
        total_meshk = len(eig_array[band_index])
        occupation_temp = 1.0 / (np.exp((np.array(eig_array[band_index]) - chemical_pot)/(boltzman_const*temperatue)) + 1)
        filling = np.sum(occupation_temp) / total_meshk
        return filling

    def find_chemical_pot_for_specific_filling(self, eig_array, band_index, temperature, target_filling, max_steps):
        initial_chemical_pot = np.min(eig_array[band_index])
        chemical_pot_temp = initial_chemical_pot
        filling = self.find_filling_specific_band(eig_array, band_index, initial_chemical_pot, temperature)
        step = 0
        while (np.abs(filling - target_filling) > 0.0001) and (step < max_steps):
            delta = (target_filling - filling) * 0.001
            chemical_pot_temp += delta
            step += 1
            filling = self.find_filling_specific_band(eig_array, band_index, chemical_pot_temp, temperature)

            print step, chemical_pot_temp, filling





    def get_electron_band(self, q_path, q_spacing):
        '''
        First, obtain q_path
        '''
        special_q_distance_list, q_distance_list, q_vec_list = self.obtain_qpath(q_path, q_spacing)

        '''
        Second, solve dynamical matrix at a q point
        '''
        
        band_structure = []
        atom_projected = []
        pos_expectation = []

        pos_expectation_nk = []
        #if self.edge_cal:
        #    position_operator = np.zeros((2*self.dimension*self.num_atom, 2*self.dimension*self.num_atom), dtype=complex)
        #    for i in range(self.num_atom):
        #        cell_number = i % self.num_repeat
        #        for j in range(self.dimension):
        #            position_operator[self.dimension*i + j, self.dimension*i + j] = cell_number
        #            position_operator[self.dimension*i + j + self.dimension*self.num_atom, self.dimension*i + j + self.dimension*self.num_atom] = cell_number

        for i in range(len(q_vec_list)):
            print 'Process: ' + str(i+1) +'/' + str(len(q_vec_list))
            q_vec = q_vec_list[i]
            H = self.construct_H_q(q_vec)
            w1, v1 = np.linalg.eigh(H)
            band_num = len(w1)
            band_structure.append(w1)

            """atom projection module"""

            atom_projected_nk = []
            for j in range(band_num):
                wave_square = np.multiply(v1[:,j].transpose(), np.conjugate(v1[:,j].transpose()))
                atom_temp = []
                for k in range(self.num_atom):
                    projection = np.sum(wave_square[k])
                    atom_temp.append(np.real(projection))
                #print np.sum(atom_temp)
                atom_projected_nk.append(atom_temp)

            atom_projected.append(atom_projected_nk)

            """atom projection module"""

            """position expectation module"""
            #if self.edge_cal:
            #    pos_expectation_nk = []
            #    for j in range(band_num):
            #        expectation = np.matmul(np.conjugate(v1[:,j]), np.matmul(position_operator, v1[:,j].transpose()))
            #        #expectation = np.matmul(np.conjugate(v1[j]), v1[j].transpose())
            #        pos_expectation_nk.append(expectation)
            #    pos_expectation.append(pos_expectation_nk)


        print 'total number of band is ' + str(band_num)


        '''
        Third, write electron band file
        '''

        out_name = 'eigenvalue.out'
        g = open(out_name,'w')
        out_name2 = 'eigenvalue_projected.out'
        g2 = open(out_name2,'w')
        #if self.edge_cal:
        #    print "Edge calculations: position_expectation calcualtion"
        #    out_name3 = 'ph_frequecny_'+self.out_tag+'_pos_expectation.out'
        #    g3 = open(out_name3, 'w')

        templine = ''

        for i in range(len(special_q_distance_list)):
            templine += str(special_q_distance_list[i])+ ' '
        templine += '\n'
        g.write(templine)
        g2.write(templine)
        if self.edge_cal:
            g3.write(templine)

        for i in range(len(q_vec_list)):
            templine = str(q_distance_list[i])
            for j in range(band_num):
                templine += ' '+ str(band_structure[i][j])
            templine += '\n'    
            g.write(templine)
        g.close()

        for i in range(len(q_vec_list)):
            for j in range(band_num):
                templine = str(q_distance_list[i]) + ' ' + str(band_structure[i][j])
                for k in range(self.num_atom):
                    templine += ' ' + str(atom_projected[i][j][k])
                templine += '\n'
                g2.write(templine)
            g2.write('\n')
        g2.close()

        #if self.edge_cal:
        #    for i in range(len(q_vec_list)):
        #        for j in range(band_num):
        #            templine = str(q_distance_list[i]) + ' ' + str(band_structure[i][j]) + ' ' + str(pos_expectation[i][j])
        #            templine += '\n'
        #            g3.write(templine)
        #        g3.write('\n')
        #    g3.close()

        return 0

    def draw_electron_band(self):
        '''
        Fourth, draw electron band along q path
        '''
        file_name = 'eigenvalue.out'
        f = open(file_name,'r')
        tempf = f.readlines()
        f.close()

        totalline = len(tempf)
        #print totalline
        band_num = len(tempf[1].split()) - 1


        sqx = [float(tempf[0].split()[i]) for i in range(len(tempf[0].split()))]

        #print sqx
        fig = plt.figure()
        plt.axhline(y=0, color='black', linewidth=2)
        for i in range(len(sqx)):
            plt.axvline(x=sqx[i], color='black', linewidth=2)

        qx = []
        eigenval = np.zeros((band_num, totalline-1))


        for i in range(1, totalline):
            temp_val = tempf[i].split()
            qx.append(float(temp_val[0]))
            for j in range(band_num):
                eigenval[j][i-1] = float(temp_val[1+j])


        for i in range(band_num):
            plt.plot(qx, eigenval[i], color='black')

        #plt.ylim(0, max(eigenval[:][:]))
        plt.xlim(min(sqx)-0.1, max(sqx)+0.1)
        fig.savefig('el_band.png')
        plt.show()
        return 0



class ManybodyInteraction_MFT:
    def __init__(self, TBmodel):
        self.dimension = TBmodel.dimension
        self.num_atom = TBmodel.num_atom
        self.onsite_info = TBmodel.onsite_info
        self.hopping_info = TBmodel.hopping_info
        self.orderpara_info = []
        self.orderpara_type_info = []
        self.MB_interaction_info = []
        self.spin = TBmodel.spin
        self.recip_vec = TBmodel.recip_vec
        self.latt_vec = TBmodel.latt_vec
        self.atom_pos =TBmodel.atom_pos
        self.boltzman_const = 8.617343e-5 # eV/K

    def set_order_parameter_type(self, iatom, jatom, supercell_of_jatom, value_type):
        if len(supercell_of_jatom) != self.dimension:
            print 'Please check either dimension or the size of supercell; They are different to each other'
            return 0
        orderpara_type_temp = [iatom, jatom, supercell_of_jatom, value_type]
        self.orderpara_type_info.append(orderpara_type_temp)
        return 0

    def set_MB_interactions(self, iatom, jatom, supercell_of_jatom, interact_strength, order_para_type):
        if len(supercell_of_jatom) != self.dimension:
            print 'Please check either dimension or the size of supercell; They are different to each other'
            return 0

        MB_interaction_temp = [iatom, jatom, supercell_of_jatom, interact_strength, order_para_type]

        self.MB_interaction_info.append(MB_interaction_temp)
        return 0

    def find_hopping_for_pair_MFT(self, iatom, jatom):
        proper_hopping_info = []  # [r_j-r_i, hopping]

        if iatom == jatom:
            for i in range(len(self.onsite_info)):
                proper_hopping_info.append([self.onsite_info[i][2], self.onsite_info[i][3]])

            for i in range(len(self.hopping_info)):
                if (iatom == self.hopping_info[i][0] and iatom == self.hopping_info[i][1]):
                    diff_r = np.array(self.atom_pos[jatom]) + np.array(self.hopping_info[i][2]).transpose() - np.array(self.atom_pos[iatom])
                    proper_hopping_info.append([diff_r, self.hopping_info[i][3]])
            
            for i in range(len(self.orderpara_info)):
                if (iatom == self.orderpara_info[i][0] and iatom == self.orderpara_info[i][1]):
                    diff_r = np.array(self.atom_pos[jatom]) + np.array(self.orderpara_info[i][2]).transpose() - np.array(self.atom_pos[iatom])
                    proper_hopping_info.append([diff_r, self.orderpara_info[i][3]])              
        else:
            for i in range(len(self.hopping_info)):
                if (iatom == self.hopping_info[i][0] and jatom == self.hopping_info[i][1]):
                    diff_r = np.array(self.atom_pos[jatom]) + np.array(self.hopping_info[i][2]).transpose() - np.array(self.atom_pos[iatom])
                    proper_hopping_info.append([diff_r, self.hopping_info[i][3]])
                if (jatom == self.hopping_info[i][0] and iatom == self.hopping_info[i][1]):
                    diff_r = np.array(self.atom_pos[jatom])  - np.array(self.atom_pos[iatom]) -  np.array(self.hopping_info[i][2]).transpose()
                    proper_hopping_info.append([diff_r, self.hopping_info[i][3]])
            
            for i in range(len(self.orderpara_info)):
                if (iatom == self.orderpara_info[i][0] and jatom == self.orderpara_info[i][1]):
                    diff_r = np.array(self.atom_pos[jatom]) + np.array(self.horderpara_info[i][2]).transpose() - np.array(self.atom_pos[iatom])
                    proper_hopping_info.append([diff_r, self.orderpara_info[i][3]])
                if (jatom == self.orderpara_info[i][0] and iatom == self.orderpara_info[i][1]):
                    diff_r = np.array(self.atom_pos[jatom])  - np.array(self.atom_pos[iatom]) -  np.array(self.orderpara_info[i][2]).transpose()
                    proper_hopping_info.append([diff_r, self.orderpara_info[i][3]])
        
        return proper_hopping_info


    def construct_H_q_MFT(self, q_vec):
        #recip_vec = self.reciprocal()
        q = np.dot(self.recip_vec.transpose(), np.array(q_vec).transpose())
        #q = np.array(q_vec)
        h = np.zeros((self.spin * self.num_atom, self.spin * self.num_atom), dtype=complex)
        for i in range(self.num_atom):
            for j in range(self.num_atom):
                if i <= j:
                    proper_hopping_info = self.find_hopping_for_pair_MFT(i,j)
                    h_local = 0.0+0.0j
                    for k in range(len(proper_hopping_info)):
                        #r = np.array(proper_fc_info[k][0])
                        r = np.dot(self.latt_vec.transpose(), np.array(proper_hopping_info[k][0]).transpose())
                        #print r
                        phase_factor = np.exp(np.vdot(r, q) * 1j)
                        h_local += proper_hopping_info[k][1] * phase_factor
                    h[i, j] += h_local
                    if i != j:
                        h[j,i] += h_local.conj()

        hamiltonian = (h+ h.conj().transpose()) / 2.0 

        return hamiltonian

    def get_qpoint_mesh(self, qmesh):
        if self.dimension != len(qmesh):
            print 'Check either dimension or q_point_mesh'
            return 0
        
        q_vec_list= []

        if self.dimension ==2:
            for i in range(int(qmesh[0])):
                for j in range(int(qmesh[1])):
                    qtemp = [0.0 + i*(1.0/int(qmesh[0])), 0.0 + j*(1.0/int(qmesh[1]))]
                    q_vec_list.append(qtemp)
        if self.dimension ==3:
            for i in range(int(qmesh[0])):
                for j in range(int(qmesh[1])):
                    for k in range(int(qmesh[2])):
                        qtemp = [0.0 + i*(1.0/int(qmesh[0])), 0.0 + j*(1.0/int(qmesh[1])), 0.0 + k*(1.0/int(qmesh[2]))]
                        q_vec_list.append(qtemp)

        return q_vec_list


    def find_Fermi_energy_zerotemp(self, eigval, q_vec_list, filling_factor):
        sort_eigenvalue = np.sort(np.array(eigval).ravel())

        tot_elec = self.num_atom * filling_factor * len(q_vec_list)
        #print len(sort_eigenvalue)

        Fermi_energy = (sort_eigenvalue[int(tot_elec)] + sort_eigenvalue[int(tot_elec)+1]) / 2.0

        return Fermi_energy


    def calculate_new_orderpara_set(self, eigval, eigvec, q_vec_list, Fermi_energy, temperature):
        new_orderpara_set = np.zeros(len(self.orderpara_info), dtype=complex)
        beta = 1.0 / (temperature * self.boltzman_const)
        degeneracy = 2.0 / self.spin # spinor = True --> degeneracy = 1 spinor False --> degeneracy = 2
        num_mesh = len(eigval)
        num_eig = len(eigval[0])
        #print num_mesh ; print num_eig
        new_orderpara_set = []
        for i in range(self.num_orderpara):
            temp_order = 0.0+0.0j
            iatom = self.orderpara_type_info[i][0] ; jatom = self.orderpara_type_info[i][1]  ; supercell_of_jatom = self.orderpara_type_info[i][2]
            for j in range(num_eig):
                for k in range(num_mesh):
                    r = np.dot(self.latt_vec.transpose(), np.array(supercell_of_jatom).transpose())
                    q = np.dot(self.recip_vec.transpose(), np.array(q_vec_list[k]).transpose())
                    additional_phase_factor = np.exp(np.vdot(r, q) * 1j)
                    #print q_vec_list[k], supercell_of_jatom, additional_phase_factor
                    temp_order += np.dot(eigvec[k][j][iatom].conj().transpose(), eigvec[k][j][jatom]) * (1.0 / (1.0 + np.exp(beta * (eigval[k][j]-Fermi_energy)))) * additional_phase_factor
            temp_order = temp_order / num_mesh
            new_orderpara_set.append(temp_order)
        return np.array(new_orderpara_set)

    def calculate_total_energy(self, eigval, Fermi_energy, temperature, orderpara):
        beta = 1.0 / (temperature * self.boltzman_const)
        degeneracy = 2.0 / self.spin # spinor = True --> degeneracy = 1 spinor False --> degeneracy = 2
        num_mesh = len(eigval)
        num_eig = len(eigval[0])
        total_energy = 0
        ##########################
        for i in range(num_eig):
            for j in range(num_mesh):
                total_energy += degeneracy * eigval[j][i] * (1.0 / (1.0 + np.exp(beta * (eigval[j][i]-Fermi_energy))))
        total_energy = total_energy / num_mesh

        ##########################
        for i in range(num_eig):
            pass



        return total_energy

    def impose_constraints(self):
        '''
        To be implemented ; it reduces the number of order parameters by imposing constraints which are physical meaningful
        '''
        return 0

    def sc_solver(self, q_point_mesh, max_steps, threshold, filling_factor, temperature, mixing_ratio):
        ### step 1: prepare random order parameters
        self.num_orderpara = len(self.orderpara_type_info)
        initial_random_orderpara_set = []
        for i in range(self.num_orderpara):
            if self.orderpara_type_info[i][3] == 'real' or self.orderpara_type_info[i][3] == 'Real' or self.orderpara_type_info[i][3] == 'REAL':        
                temp = np.random.rand()
                initial_random_orderpara_set.append(temp)    
            elif self.orderpara_type_info[i][3] == 'complex' or self.orderpara_type_info[i][3] == 'Complex' or self.orderpara_type_info[i][3] == 'COMPLEX':
                temp = np.random.rand() + 1.0j*np.random.rand()
                initial_random_orderpara_set.append(temp)   
        initial_random_orderpara_set = np.random.rand(self.num_orderpara)
        initial_random_orderpara_set = np.array([0.5, 0.5, 1.0j, 1.0j, 1.0j, -1.0j, -1.0j, -1.0j])

        q_vec_list = self.get_qpoint_mesh(q_point_mesh)


        ### step 2: sc solve (solve TB --> find Fermi level --> get new order parameters --> compare order paremeters --> prepare next values)
        old_orderpara_set = initial_random_orderpara_set

        LCONV = False
        sc_index = 1
        output_save = []
        while (sc_index < max_steps):
            ### prepare orderpara_info
            self.orderpara_info = [] # initialize
            for i in range(len(self.MB_interaction_info)):
                temp = [self.MB_interaction_info[i][0], self.MB_interaction_info[i][1], self.MB_interaction_info[i][2], self.MB_interaction_info[i][3]*old_orderpara_set[self.MB_interaction_info[i][4]]]
                self.orderpara_info.append(temp)

            ### solve TB
            eigval = []
            eigvec = []
            for i in range(len(q_vec_list)):
                #print 'Process: ' + str(i+1) +'/' + str(len(q_vec_list))
                q_vec = q_vec_list[i]
                H = self.construct_H_q_MFT(q_vec)
                w1, v1 = np.linalg.eigh(H)
                eigval_temp = []
                eigvec_temp = []
                for j in range(len(w1)):
                    eigval_temp.append(w1[j])
                    eigvec_temp.append(v1[:,j]) 
                eigval.append(eigval_temp)
                eigvec.append(eigvec_temp)


            ### find Fermi level by using filling factor

            Fermi_energy = self.find_Fermi_energy_zerotemp(eigval, q_vec_list, filling_factor)
            #print Fermi_energy

            ### calculate total energy

            total_energy = self.calculate_total_energy(eigval, Fermi_energy, temperature,old_orderpara_set)
            #print total_energy

            #output_save.append([sc_index, Fermi_energy, total_energy, old_orderpara_set])
            output_save.append([sc_index, Fermi_energy, total_energy, np.abs(old_orderpara_set), np.angle(old_orderpara_set, deg=True)])

            ### get new order parameters

            new_orderpara_set = self.calculate_new_orderpara_set(eigval, eigvec, q_vec_list, Fermi_energy, temperature)

            ### calculate error between new parameters with old paramters

            error = new_orderpara_set - old_orderpara_set
            
            temp_line_error = ''
            temp_line_order_parameter = ''
            for i in range(len(error)):
                temp_line_error += str(np.abs(error[i])) + ' '
                temp_line_order_parameter += str(new_orderpara_set[i]) + ' '
            #print temp_line_error
            #print temp_line_order_parameter
            if sc_index == 1:
                energy_error = total_energy
            else:
                energy_error = output_save[sc_index-1][2] - output_save[sc_index-2][2]
            print 'SCF loop: ' + str(sc_index) + '/' + str(max_steps) + ' & ' + 'average SCF error: ' + str(np.average(np.abs(error))) + ' & ' + 'energy error: ' + str(energy_error)
            
            
            ### SCF convergence test

            if np.all(np.abs(error) < threshold):
                LCONV = True
            if LCONV:
                break
            ### prepare next values by using error
            #next_orderpara_set_real = np.real(old_orderpara_set) * (1.0 - np.real(error)) + np.real(new_orderpara_set) * np.real(error)
            #next_orderpara_set_imag = np.imag(old_orderpara_set) * (1.0 - np.imag(error)) + np.imag(new_orderpara_set) * np.imag(error)
            #print next_orderpara_set_real, next_orderpara_set_imag
            #next_orderpara_set = old_orderpara_set * (1.0-np.absolute(error)) + new_orderpara_set * np.absolute(error)
            next_orderpara_set = old_orderpara_set * (1.0 - mixing_ratio) + new_orderpara_set * mixing_ratio

            old_orderpara_set = next_orderpara_set
            sc_index += 1

        #### last_calculation
        #self.orderpara_info = [] # initialize
        #for i in range(len(self.MB_interaction_info)):
        #    temp = [self.MB_interaction_info[i][0], self.MB_interaction_info[i][1], self.MB_interaction_info[i][2], self.MB_interaction_info[i][3]*new_orderpara_set[self.MB_interaction_info[i][4]]]
        #    self.orderpara_info.append(temp)
        #eigval = []
        #eigvec = []
        #for i in range(len(q_vec_list)):
        #    #print 'Process: ' + str(i+1) +'/' + str(len(q_vec_list))
        #    q_vec = q_vec_list[i]
        #    H = self.construct_H_q_MFT(q_vec)
        #    w1, v1 = np.linalg.eigh(H)
        #    eigval_temp = []
        #    eigvec_temp = []
        #    for j in range(len(w1)):
        #        eigval_temp.append(w1[j])
        #        eigvec_temp.append(v1[:,j]) 
        #    eigval.append(eigval_temp)
        #    eigvec.append(eigvec_temp)
        #Fermi_energy = self.find_Fermi_energy_zerotemp(eigval, q_vec_list, filling_factor)
        #total_energy = self.calculate_total_energy(eigval, Fermi_energy, temperature)
        ##output_save.append([sc_index, Fermi_energy, total_energy, new_orderpara_set])
        #output_save.append([sc_index, Fermi_energy, total_energy, np.abs(old_orderpara_set), np.angle(old_orderpara_set, deg=True)])



        ### step 3: print process

        #time_tag = str(dt.datetime.now().year) + str(dt.datetime.now().month) + str(dt.datetime.now().day) + str(dt.datetime.now().hour) + str(dt.datetime.now().minute) +str(dt.datetime.now().second)
        time_tag = '{0:04d}{1:02d}{2:02d}{3:02d}{4:02d}{5:02d}'.format(dt.datetime.now().year, dt.datetime.now().month, dt.datetime.now().day, dt.datetime.now().hour, dt.datetime.now().minute, dt.datetime.now().second)
        output_name = 'orderparameter_info_' + time_tag + '.out'
        g = open(output_name, 'w')

        for i in range(len(output_save)):
            temp = str(output_save[i][0]) + '\t' + str(output_save[i][1]) + '\t' + str(output_save[i][2])
            for j in range(len(output_save[i][3])):
                temp += '\t' + str(output_save[i][3][j]) + '\t' + str(output_save[i][4][j])
            temp += '\n'
            g.write(temp)
        g.close()


        ### step 4: merge orderpara_info into hopping_info and replace it 

        self.obtain_final_info()

        self.hopping_info = self.merged_hopping_info

        return 0

    def obtain_final_info(self):
        self.merged_hopping_info = []
        for i in range(len(self.hopping_info)):
            self.merged_hopping_info.append(self.hopping_info[i])
        for i in range(len(self.orderpara_info)):
            self.merged_hopping_info.append(self.orderpara_info[i])
        return 0





if __name__ == "__main__":
    lat = [[1,   -np.sqrt(3)], [1,   np.sqrt(3)]]
    orb = [[1.0/3, 2.0/3], [2.0/3, 1.0/3]]
    spinor = False
    test =  electronTB(2, 2, spinor)
    test.set_geometry(lat, orb)
    test.set_onsite([.0,.0])
    NN_hopping = -1.0
    test.set_hopping(0,1,[0.0,0.0],NN_hopping)
    test.set_hopping(0,1,[-1.0,0.0],NN_hopping)
    test.set_hopping(0,1,[0.0,1.0],NN_hopping)
    #test.print_info()
    ####################
    q_path_line = [[0, 0], [0.5, 0.0], [1.0/3, 1.0/3], [0.0, 0]]
    q_spacing_line = 20
    #test.obtain_qpath(q_path_line, q_spacing_line)
    #test.get_electron_band(q_path_line, q_spacing_line)
    #test.draw_electron_band()
    q_mesh = [30,30]
    max_steps = 20
    threshold = 1e-4
    filling_factor = 1.0/2
    temperature = 1e-10
    #print test.spin

    #print np.dot(test.latt_vec.T, test.recip_vec)

    MFT_test = ManybodyInteraction_MFT(test)

    MFT_test.set_order_parameter_type(0,0, [0,0])
    MFT_test.set_order_parameter_type(1,1, [0,0])

    MFT_test.set_order_parameter_type(1,1, [-1,0])
    MFT_test.set_order_parameter_type(1,1, [0,-1])
    MFT_test.set_order_parameter_type(1,1, [-1,-1])

    MFT_test.set_order_parameter_type(0,0, [-1,0])
    MFT_test.set_order_parameter_type(0,0, [0,-1])
    MFT_test.set_order_parameter_type(0,0, [-1,-1])

    V_1 = NN_hopping / 0.2
    V_2 = NN_hopping / 0.2

    MFT_test.set_MB_interactions(1, 1, [0,0], V_1, 0)
    MFT_test.set_MB_interactions(0, 0, [0,0], V_1, 1)

    MFT_test.set_MB_interactions(1, 1, [1,0], V_2, 2)
    MFT_test.set_MB_interactions(1, 1, [0,1], V_2, 3)
    MFT_test.set_MB_interactions(1, 1, [1,1], V_2, 4)

    MFT_test.set_MB_interactions(0, 0, [1,0], V_2, 5)
    MFT_test.set_MB_interactions(0, 0, [0,1], V_2, 6)
    MFT_test.set_MB_interactions(0, 0, [1,1], V_2, 7)

    MFT_test.sc_solver(q_mesh, max_steps, threshold, filling_factor, temperature)
    #print MFT_test.obtain_final_info()


